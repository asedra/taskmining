"""
Memory Manager Module
====================

Handles persistent storage and retrieval of project ideas, context, and search functionality.
"""

import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..models import ProjectIdea

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages persistent memory for PM Assistant
    
    Provides storage, retrieval, and search capabilities for project ideas,
    context, and historical data.
    """
    
    def __init__(self, db_path: str = "data/pm_assistant.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        self._init_database()
        logger.info(f"Memory Manager initialized with database: {db_path}")
    
    def _init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Project ideas table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_ideas (
                    id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    tags TEXT,  -- JSON array
                    jira_ref TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Project context table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_context (
                    project_name TEXT PRIMARY KEY,
                    context_data TEXT,  -- JSON object
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Search index table for semantic search
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_index (
                    idea_id TEXT PRIMARY KEY,
                    search_text TEXT NOT NULL,
                    keywords TEXT,  -- JSON array
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (idea_id) REFERENCES project_ideas (id)
                )
            """)
            
            # Activity log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    activity_data TEXT,  -- JSON object
                    timestamp TEXT NOT NULL
                )
            """)
            
            conn.commit()
            logger.info("Database schema initialized")
    
    def store_idea(self, idea: ProjectIdea, project_name: str = None) -> bool:
        """
        Store a project idea in memory
        
        Args:
            idea: ProjectIdea object to store
            project_name: Project name (optional, will use idea's project if available)
            
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO project_ideas 
                    (id, project_name, summary, description, category, priority, tags, jira_ref, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    idea.id,
                    project_name or "default",
                    idea.summary,
                    idea.description,
                    idea.category,
                    idea.priority,
                    json.dumps(idea.tags),
                    idea.jira_ref,
                    idea.created_at,
                    idea.updated_at
                ))
                
                # Update search index
                search_text = f"{idea.summary} {idea.description}".lower()
                keywords = self._extract_keywords(search_text)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO search_index 
                    (idea_id, search_text, keywords, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    idea.id,
                    search_text,
                    json.dumps(keywords),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
                # Log activity
                self._log_activity(project_name or "default", "idea_stored", {
                    "idea_id": idea.id,
                    "category": idea.category,
                    "summary": idea.summary
                })
                
                logger.info(f"Stored idea: {idea.id}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing idea {idea.id}: {str(e)}")
            return False
    
    def get_idea(self, idea_id: str) -> Optional[ProjectIdea]:
        """
        Retrieve a specific project idea
        
        Args:
            idea_id: Unique identifier for the idea
            
        Returns:
            ProjectIdea object or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, summary, description, category, priority, tags, jira_ref, created_at, updated_at
                    FROM project_ideas 
                    WHERE id = ?
                """, (idea_id,))
                
                row = cursor.fetchone()
                if row:
                    return ProjectIdea(
                        id=row[0],
                        summary=row[1],
                        description=row[2],
                        category=row[3],
                        priority=row[4],
                        tags=json.loads(row[5]) if row[5] else [],
                        jira_ref=row[6],
                        created_at=row[7],
                        updated_at=row[8]
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving idea {idea_id}: {str(e)}")
            return None
    
    def update_idea(self, idea: ProjectIdea) -> bool:
        """
        Update an existing project idea
        
        Args:
            idea: Updated ProjectIdea object
            
        Returns:
            Success status
        """
        idea.updated_at = datetime.now().isoformat()
        return self.store_idea(idea)
    
    def search_ideas(self, query: str, filters: Dict[str, Any] = None) -> List[ProjectIdea]:
        """
        Search project ideas using text search and filters
        
        Args:
            query: Search query text
            filters: Optional filters (category, tags, date_range, project_name)
            
        Returns:
            List of matching ProjectIdea objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build search query
                base_query = """
                    SELECT pi.id, pi.summary, pi.description, pi.category, pi.priority, 
                           pi.tags, pi.jira_ref, pi.created_at, pi.updated_at
                    FROM project_ideas pi
                    JOIN search_index si ON pi.id = si.idea_id
                    WHERE si.search_text LIKE ?
                """
                
                params = [f"%{query.lower()}%"]
                
                # Apply filters
                if filters:
                    if filters.get('category'):
                        base_query += " AND pi.category = ?"
                        params.append(filters['category'])
                    
                    if filters.get('project_name'):
                        base_query += " AND pi.project_name = ?"
                        params.append(filters['project_name'])
                    
                    if filters.get('priority'):
                        base_query += " AND pi.priority = ?"
                        params.append(filters['priority'])
                    
                    if filters.get('jira_ref'):
                        base_query += " AND pi.jira_ref IS NOT NULL"
                
                base_query += " ORDER BY pi.updated_at DESC"
                
                cursor.execute(base_query, params)
                rows = cursor.fetchall()
                
                ideas = []
                for row in rows:
                    idea = ProjectIdea(
                        id=row[0],
                        summary=row[1],
                        description=row[2],
                        category=row[3],
                        priority=row[4],
                        tags=json.loads(row[5]) if row[5] else [],
                        jira_ref=row[6],
                        created_at=row[7],
                        updated_at=row[8]
                    )
                    ideas.append(idea)
                
                logger.info(f"Search for '{query}' returned {len(ideas)} results")
                return ideas
                
        except Exception as e:
            logger.error(f"Error searching ideas: {str(e)}")
            return []
    
    def get_all_ideas(self, project_name: str = None) -> List[ProjectIdea]:
        """
        Get all project ideas, optionally filtered by project name
        
        Args:
            project_name: Optional project name filter
            
        Returns:
            List of all ProjectIdea objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if project_name:
                    cursor.execute("""
                        SELECT id, summary, description, category, priority, tags, jira_ref, created_at, updated_at
                        FROM project_ideas 
                        WHERE project_name = ?
                        ORDER BY updated_at DESC
                    """, (project_name,))
                else:
                    cursor.execute("""
                        SELECT id, summary, description, category, priority, tags, jira_ref, created_at, updated_at
                        FROM project_ideas 
                        ORDER BY updated_at DESC
                    """)
                
                rows = cursor.fetchall()
                
                ideas = []
                for row in rows:
                    idea = ProjectIdea(
                        id=row[0],
                        summary=row[1],
                        description=row[2],
                        category=row[3],
                        priority=row[4],
                        tags=json.loads(row[5]) if row[5] else [],
                        jira_ref=row[6],
                        created_at=row[7],
                        updated_at=row[8]
                    )
                    ideas.append(idea)
                
                return ideas
                
        except Exception as e:
            logger.error(f"Error getting all ideas: {str(e)}")
            return []
    
    def get_project_context(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Get project context data
        
        Args:
            project_name: Name of the project
            
        Returns:
            Project context dictionary or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT context_data FROM project_context 
                    WHERE project_name = ?
                """, (project_name,))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting project context: {str(e)}")
            return None
    
    def save_project_context(self, project_name: str, context: Dict[str, Any]) -> bool:
        """
        Save project context data
        
        Args:
            project_name: Name of the project
            context: Context dictionary to save
            
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.now().isoformat()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO project_context 
                    (project_name, context_data, created_at, updated_at)
                    VALUES (?, ?, COALESCE((SELECT created_at FROM project_context WHERE project_name = ?), ?), ?)
                """, (project_name, json.dumps(context), project_name, now, now))
                
                conn.commit()
                
                self._log_activity(project_name, "context_saved", {
                    "keys": list(context.keys())
                })
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving project context: {str(e)}")
            return False
    
    def get_activity_log(self, project_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get activity log for a project
        
        Args:
            project_name: Name of the project
            limit: Maximum number of activities to return
            
        Returns:
            List of activity records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT activity_type, activity_data, timestamp
                    FROM activity_log 
                    WHERE project_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (project_name, limit))
                
                rows = cursor.fetchall()
                
                activities = []
                for row in rows:
                    activity = {
                        'type': row[0],
                        'data': json.loads(row[1]) if row[1] else {},
                        'timestamp': row[2]
                    }
                    activities.append(activity)
                
                return activities
                
        except Exception as e:
            logger.error(f"Error getting activity log: {str(e)}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text for search indexing
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction (can be enhanced with NLP)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        words = text.lower().split()
        keywords = [word.strip('.,!?;:"()[]{}') for word in words 
                   if len(word) > 3 and word not in stop_words]
        
        return list(set(keywords))
    
    def _log_activity(self, project_name: str, activity_type: str, data: Dict[str, Any]):
        """
        Log activity for audit trail
        
        Args:
            project_name: Name of the project
            activity_type: Type of activity
            data: Activity data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO activity_log (project_name, activity_type, activity_data, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (project_name, activity_type, json.dumps(data), datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
    
    def cleanup_old_data(self, days_old: int = 90) -> int:
        """
        Clean up old data to manage database size
        
        Args:
            days_old: Number of days after which to clean up data
            
        Returns:
            Number of records cleaned up
        """
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
            cutoff_iso = cutoff_date.isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old activity logs
                cursor.execute("""
                    DELETE FROM activity_log 
                    WHERE timestamp < ?
                """, (cutoff_iso,))
                
                cleaned_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {cleaned_count} old activity records")
                return cleaned_count
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
            return 0