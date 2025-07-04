"""
Workspace AI Assistant - Advanced AI automation for Cursor environment
Combines task mining with intelligent project management and automation
"""

import os
import json
import time
import threading
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
from activity_logger import ActivityLogger
from analyzer import Analyzer
from nlp_processor import NLPProcessor, ProjectElement
from jira_mcp_client import JiraMCPClient, JiraIssue
from chrome_ray_automation import ChromeRayAutomation
from ui_action_handler import UIActionHandler

class WorkspaceAIAssistant:
    """Main AI Assistant class for workspace automation"""
    
    def __init__(self, db_path: str = "data/workspace_ai.db"):
        self.db_path = db_path
        self.activity_logger = ActivityLogger(db_path)
        self.analyzer = Analyzer(self.activity_logger)
        self.nlp_processor = NLPProcessor()
        self.jira_client = JiraMCPClient()
        self.chrome_automation = ChromeRayAutomation()
        self.ui_handler = UIActionHandler()
        
        # Background monitoring state
        self.is_monitoring = False
        self.monitoring_threads = []
        self.user_context = {}
        self.project_elements = []
        self.quick_actions = []
        
        # Initialize database
        self._init_workspace_db()
        
    def _init_workspace_db(self):
        """Initialize workspace-specific database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Project elements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                element_type TEXT NOT NULL,
                content TEXT NOT NULL,
                structured_data TEXT,
                project_id TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Jira issues table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jira_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jira_id TEXT UNIQUE,
                issue_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                milestone TEXT,
                component TEXT,
                phase TEXT,
                priority TEXT,
                status TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # User context table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_type TEXT NOT NULL,
                context_data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                relevance_score REAL DEFAULT 1.0
            )
        ''')
        
        # Quick actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quick_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                action_data TEXT NOT NULL,
                trigger_context TEXT,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_background_monitoring(self):
        """Start the background monitoring system"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        print("🚀 Starting Workspace AI Assistant background monitoring...")
        
        # Start background threads
        threads = [
            threading.Thread(target=self._monitor_user_activities, daemon=True),
            threading.Thread(target=self._analyze_context_continuously, daemon=True),
            threading.Thread(target=self._monitor_project_changes, daemon=True),
            threading.Thread(target=self._update_quick_actions, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
            self.monitoring_threads.append(thread)
        
        print("✅ Background monitoring started successfully")
    
    def stop_background_monitoring(self):
        """Stop the background monitoring system"""
        self.is_monitoring = False
        print("⏹️  Stopping background monitoring...")
        
        # Wait for threads to finish
        for thread in self.monitoring_threads:
            if thread.is_alive():
                thread.join(timeout=2)
        
        self.monitoring_threads.clear()
        print("✅ Background monitoring stopped")
    
    def _monitor_user_activities(self):
        """Continuously monitor user activities in background"""
        while self.is_monitoring:
            try:
                # Analyze recent activities
                recent_activities = self.analyzer.get_recent_activities(minutes=10)
                
                # Extract insights from activities
                insights = self.nlp_processor.extract_insights_from_activities(recent_activities)
                
                # Store context
                self._store_user_context("activity_insights", insights)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Error in activity monitoring: {e}")
                time.sleep(60)
    
    def _analyze_context_continuously(self):
        """Continuously analyze user context and generate suggestions"""
        while self.is_monitoring:
            try:
                # Get current context
                current_context = self._get_current_context()
                
                # Analyze for patterns and suggestions
                suggestions = self.nlp_processor.generate_suggestions(current_context)
                
                # Update quick actions based on suggestions
                self._update_quick_actions_from_suggestions(suggestions)
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"Error in context analysis: {e}")
                time.sleep(300)
    
    def _monitor_project_changes(self):
        """Monitor for project-related changes and updates"""
        while self.is_monitoring:
            try:
                # Check for new project elements
                new_elements = self._detect_new_project_elements()
                
                for element in new_elements:
                    self._process_project_element(element)
                
                time.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                print(f"Error in project monitoring: {e}")
                time.sleep(120)
    
    def _update_quick_actions(self):
        """Update available quick actions based on context"""
        while self.is_monitoring:
            try:
                # Get current context
                context = self._get_current_context()
                
                # Generate contextual quick actions
                actions = self._generate_contextual_actions(context)
                
                # Update quick actions
                self._store_quick_actions(actions)
                
                time.sleep(180)  # Update every 3 minutes
                
            except Exception as e:
                print(f"Error in quick actions update: {e}")
                time.sleep(180)
    
    def process_natural_language_input(self, user_input: str) -> ProjectElement:
        """Process natural language input and extract structured elements"""
        try:
            # Use NLP processor to extract structured elements
            structured_element = self.nlp_processor.extract_project_elements(user_input)
            
            # Store the element
            self._store_project_element(structured_element)
            
            return structured_element
            
        except Exception as e:
            print(f"Error processing natural language input: {e}")
            return ProjectElement()
    
    def create_jira_issues(self, project_element: ProjectElement) -> List[JiraIssue]:
        """Convert project element to Jira issues using MCP methodology"""
        try:
            issues = []
            
            # Create Epic (Vision-level)
            if project_element.vision:
                epic = JiraIssue(
                    issue_type="Epic",
                    title=f"Epic: {project_element.vision[:50]}...",
                    description=project_element.vision,
                    priority=project_element.priority
                )
                issues.append(epic)
            
            # Create Stories (User-focused)
            for milestone in project_element.milestones:
                story = JiraIssue(
                    issue_type="Story",
                    title=f"Story: {milestone}",
                    description=f"User story for milestone: {milestone}",
                    milestone=milestone,
                    priority=project_element.priority
                )
                issues.append(story)
            
            # Create Tasks (Detailed actionable)
            for deliverable in project_element.deliverables:
                task = JiraIssue(
                    issue_type="Task",
                    title=f"Task: {deliverable}",
                    description=f"Implement deliverable: {deliverable}",
                    priority=project_element.priority
                )
                issues.append(task)
            
            # Create Jira issues via MCP client
            created_issues = []
            for issue in issues:
                jira_issue = self.jira_client.create_issue(issue)
                if jira_issue:
                    created_issues.append(jira_issue)
                    self._store_jira_issue(jira_issue)
            
            return created_issues
            
        except Exception as e:
            print(f"Error creating Jira issues: {e}")
            return []
    
    def automate_chrome_interaction(self, action_type: str, parameters: Dict[str, Any]) -> bool:
        """Automate Chrome interactions using Ray"""
        try:
            return self.chrome_automation.execute_action(action_type, parameters)
        except Exception as e:
            print(f"Error in Chrome automation: {e}")
            return False
    
    def get_quick_actions(self, context: str = "") -> List[Dict[str, Any]]:
        """Get available quick actions for current context"""
        try:
            # Get context-specific actions
            actions = self._get_quick_actions_from_db(context)
            
            # Add default actions
            default_actions = [
                {
                    "id": "create_jira_task",
                    "title": "Create Jira Task",
                    "description": "Create a Jira task from selected text",
                    "icon": "task",
                    "action_type": "jira_create"
                },
                {
                    "id": "summarize_content",
                    "title": "Summarize",
                    "description": "Summarize the selected content",
                    "icon": "summarize",
                    "action_type": "summarize"
                },
                {
                    "id": "analyze_impact",
                    "title": "Analyze Impact",
                    "description": "Analyze the impact of the selected item",
                    "icon": "analyze",
                    "action_type": "analyze"
                },
                {
                    "id": "automate_chrome",
                    "title": "Automate in Chrome",
                    "description": "Automate this action in Chrome",
                    "icon": "automation",
                    "action_type": "chrome_automation"
                }
            ]
            
            return actions + default_actions
            
        except Exception as e:
            print(f"Error getting quick actions: {e}")
            return []
    
    def execute_quick_action(self, action_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a quick action"""
        try:
            return self.ui_handler.execute_action(action_id, context_data)
        except Exception as e:
            print(f"Error executing quick action: {e}")
            return {"success": False, "error": str(e)}
    
    def _store_project_element(self, element: ProjectElement):
        """Store project element in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO project_elements 
            (timestamp, element_type, content, structured_data, project_id, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            "project_element",
            element.vision,
            json.dumps(asdict(element)),
            element.category,
            "active"
        ))
        
        conn.commit()
        conn.close()
    
    def _store_jira_issue(self, issue: JiraIssue):
        """Store Jira issue in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO jira_issues 
            (jira_id, issue_type, title, description, milestone, component, phase, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            issue.title,  # Using title as ID for now
            issue.issue_type,
            issue.title,
            issue.description,
            issue.milestone,
            issue.component,
            issue.phase,
            issue.priority,
            "created",
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _store_user_context(self, context_type: str, context_data: Any):
        """Store user context data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_context 
            (context_type, context_data, timestamp, relevance_score)
            VALUES (?, ?, ?, ?)
        ''', (
            context_type,
            json.dumps(context_data),
            datetime.now().isoformat(),
            1.0
        ))
        
        conn.commit()
        conn.close()
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current user context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent context (last 24 hours)
        cursor.execute('''
            SELECT context_type, context_data, relevance_score 
            FROM user_context 
            WHERE timestamp > datetime('now', '-24 hours')
            ORDER BY relevance_score DESC, timestamp DESC
            LIMIT 50
        ''')
        
        context = {}
        for row in cursor.fetchall():
            context_type, context_data, relevance_score = row
            if context_type not in context:
                context[context_type] = []
            context[context_type].append({
                "data": json.loads(context_data),
                "relevance": relevance_score
            })
        
        conn.close()
        return context
    
    def _detect_new_project_elements(self) -> List[str]:
        """Detect new project elements from recent activities"""
        # This would analyze recent activities for project-related content
        # For now, return empty list
        return []
    
    def _process_project_element(self, element: str):
        """Process a detected project element"""
        # Extract structured data from the element
        structured_element = self.process_natural_language_input(element)
        
        # Optionally create Jira issues
        if structured_element.vision:
            self.create_jira_issues(structured_element)
    
    def _generate_contextual_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contextual quick actions based on current context"""
        actions = []
        
        # Analyze context and generate relevant actions
        if "activity_insights" in context:
            actions.append({
                "id": "optimize_workflow",
                "title": "Optimize Workflow",
                "description": "Optimize your current workflow based on activity patterns",
                "action_type": "workflow_optimization",
                "context": "activity_insights"
            })
        
        return actions
    
    def _store_quick_actions(self, actions: List[Dict[str, Any]]):
        """Store quick actions in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for action in actions:
            cursor.execute('''
                INSERT OR REPLACE INTO quick_actions 
                (action_type, action_data, trigger_context, usage_count, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                action["action_type"],
                json.dumps(action),
                action.get("context", ""),
                0,
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def _get_quick_actions_from_db(self, context: str) -> List[Dict[str, Any]]:
        """Get quick actions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT action_data, usage_count 
            FROM quick_actions 
            WHERE trigger_context = ? OR trigger_context = ''
            ORDER BY usage_count DESC
            LIMIT 10
        ''', (context,))
        
        actions = []
        for row in cursor.fetchall():
            action_data, usage_count = row
            action = json.loads(action_data)
            action["usage_count"] = usage_count
            actions.append(action)
        
        conn.close()
        return actions
    
    def _update_quick_actions_from_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Update quick actions based on AI suggestions"""
        actions = []
        
        for suggestion in suggestions:
            action = {
                "id": f"suggestion_{suggestion.get('id', 'unknown')}",
                "title": suggestion.get("title", "AI Suggestion"),
                "description": suggestion.get("description", ""),
                "action_type": "ai_suggestion",
                "suggestion_data": suggestion
            }
            actions.append(action)
        
        self._store_quick_actions(actions)

# Singleton instance
workspace_ai = WorkspaceAIAssistant()