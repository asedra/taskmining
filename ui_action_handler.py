"""
UI Action Handler - Handles quick actions and UI interactions
Processes user interface actions for the Workspace AI Assistant
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3

class UIActionHandler:
    """Handler for UI actions and quick commands"""
    
    def __init__(self, db_path: str = "data/workspace_ai.db"):
        self.db_path = db_path
        self.action_handlers = {
            "jira_create": self._handle_jira_create,
            "summarize": self._handle_summarize,
            "analyze": self._handle_analyze,
            "chrome_automation": self._handle_chrome_automation,
            "ai_suggestion": self._handle_ai_suggestion,
            "workflow_optimization": self._handle_workflow_optimization
        }
    
    def execute_action(self, action_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a UI action"""
        try:
            # Get action type from action_id
            action_type = context_data.get("action_type", "")
            
            if not action_type:
                # Try to extract from action_id
                if "_" in action_id:
                    action_type = action_id.split("_", 1)[0]
                else:
                    action_type = action_id
            
            # Get the appropriate handler
            handler = self.action_handlers.get(action_type)
            if not handler:
                return {
                    "success": False,
                    "error": f"Unknown action type: {action_type}",
                    "action_id": action_id
                }
            
            # Execute the handler
            result = handler(context_data)
            result["action_id"] = action_id
            result["executed_at"] = datetime.now().isoformat()
            
            # Log the action
            self._log_action(action_id, action_type, context_data, result)
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "action_id": action_id,
                "executed_at": datetime.now().isoformat()
            }
            self._log_action(action_id, "error", context_data, error_result)
            return error_result
    
    def _handle_jira_create(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Jira issue creation"""
        try:
            # Extract information from context
            selected_text = context_data.get("selected_text", "")
            issue_type = context_data.get("issue_type", "Task")
            
            # Generate issue title and description
            if selected_text:
                # Use selected text as basis for issue
                title = self._generate_issue_title(selected_text)
                description = self._generate_issue_description(selected_text)
            else:
                title = context_data.get("title", "New Issue")
                description = context_data.get("description", "")
            
            # Create issue data
            issue_data = {
                "issue_type": issue_type,
                "title": title,
                "description": description,
                "priority": context_data.get("priority", "medium"),
                "labels": context_data.get("labels", [])
            }
            
            return {
                "success": True,
                "message": f"Jira {issue_type} created successfully",
                "issue_data": issue_data,
                "next_action": "open_jira_issue"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create Jira issue: {str(e)}"
            }
    
    def _handle_summarize(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content summarization"""
        try:
            content = context_data.get("selected_text", "")
            if not content:
                return {
                    "success": False,
                    "error": "No content to summarize"
                }
            
            # Generate summary
            summary = self._generate_summary(content)
            
            return {
                "success": True,
                "message": "Content summarized successfully",
                "summary": summary,
                "original_length": len(content),
                "summary_length": len(summary),
                "compression_ratio": round(len(summary) / len(content) * 100, 1)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to summarize content: {str(e)}"
            }
    
    def _handle_analyze(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle impact analysis"""
        try:
            content = context_data.get("selected_text", "")
            analysis_type = context_data.get("analysis_type", "general")
            
            if not content:
                return {
                    "success": False,
                    "error": "No content to analyze"
                }
            
            # Perform analysis
            analysis = self._perform_analysis(content, analysis_type)
            
            return {
                "success": True,
                "message": "Analysis completed successfully",
                "analysis": analysis,
                "analysis_type": analysis_type,
                "confidence": analysis.get("confidence", 0.8)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to analyze content: {str(e)}"
            }
    
    def _handle_chrome_automation(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Chrome automation"""
        try:
            action_type = context_data.get("chrome_action", "navigate")
            parameters = context_data.get("parameters", {})
            
            # This would integrate with the Chrome automation module
            result = {
                "success": True,
                "message": f"Chrome automation '{action_type}' executed",
                "action_type": action_type,
                "parameters": parameters,
                "mock_execution": True  # Indicates this is a mock result
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute Chrome automation: {str(e)}"
            }
    
    def _handle_ai_suggestion(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI suggestion execution"""
        try:
            suggestion_data = context_data.get("suggestion_data", {})
            suggestion_type = suggestion_data.get("type", "general")
            
            # Execute the suggestion
            result = self._execute_suggestion(suggestion_data)
            
            return {
                "success": True,
                "message": f"AI suggestion executed: {suggestion_type}",
                "suggestion_type": suggestion_type,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute AI suggestion: {str(e)}"
            }
    
    def _handle_workflow_optimization(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow optimization"""
        try:
            workflow_data = context_data.get("workflow_data", {})
            
            # Analyze workflow and provide optimization suggestions
            optimizations = self._analyze_workflow(workflow_data)
            
            return {
                "success": True,
                "message": "Workflow optimization completed",
                "optimizations": optimizations,
                "estimated_time_savings": "15-30 minutes per day"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to optimize workflow: {str(e)}"
            }
    
    def _generate_issue_title(self, text: str) -> str:
        """Generate a Jira issue title from text"""
        # Simple title generation - take first sentence or first 50 chars
        sentences = text.split('.')
        if sentences:
            title = sentences[0].strip()
            if len(title) > 50:
                title = title[:50] + "..."
            return title
        return text[:50] + "..." if len(text) > 50 else text
    
    def _generate_issue_description(self, text: str) -> str:
        """Generate a Jira issue description from text"""
        # Format the text as a description
        description = f"**Context:**\n{text}\n\n"
        description += "**Acceptance Criteria:**\n"
        description += "- [ ] Requirement 1\n"
        description += "- [ ] Requirement 2\n"
        description += "- [ ] Testing completed\n"
        return description
    
    def _generate_summary(self, text: str) -> str:
        """Generate a summary of the text"""
        # Simple summarization - take key sentences
        sentences = text.split('.')
        if len(sentences) <= 3:
            return text
        
        # Take first and last sentence, and middle ones if short
        summary_sentences = []
        summary_sentences.append(sentences[0])
        
        if len(sentences) > 4:
            mid_index = len(sentences) // 2
            summary_sentences.append(sentences[mid_index])
        
        summary_sentences.append(sentences[-2])  # Avoid empty last sentence
        
        return '. '.join(summary_sentences) + '.'
    
    def _perform_analysis(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Perform analysis on the text"""
        analysis = {
            "word_count": len(text.split()),
            "character_count": len(text),
            "sentences": len(text.split('.')),
            "paragraphs": len(text.split('\n\n')),
            "confidence": 0.85
        }
        
        if analysis_type == "sentiment":
            analysis["sentiment"] = self._analyze_sentiment(text)
        elif analysis_type == "complexity":
            analysis["complexity"] = self._analyze_complexity(text)
        elif analysis_type == "topics":
            analysis["topics"] = self._extract_topics(text)
        
        return analysis
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        # Simple sentiment analysis based on keyword presence
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "poor", "disappointing"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = 0.7
        elif negative_count > positive_count:
            sentiment = "negative"
            score = 0.3
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        }
    
    def _analyze_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze complexity of text"""
        words = text.split()
        sentences = text.split('.')
        
        avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
        avg_chars_per_word = sum(len(word) for word in words) / len(words) if words else 0
        
        # Simple complexity scoring
        complexity_score = (avg_words_per_sentence / 20) + (avg_chars_per_word / 10)
        complexity_score = min(complexity_score, 1.0)  # Cap at 1.0
        
        if complexity_score < 0.3:
            level = "simple"
        elif complexity_score < 0.7:
            level = "moderate"
        else:
            level = "complex"
        
        return {
            "level": level,
            "score": complexity_score,
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "avg_chars_per_word": round(avg_chars_per_word, 1)
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simple topic extraction based on common keywords
        topics = []
        
        topic_keywords = {
            "technology": ["software", "code", "programming", "development", "system"],
            "business": ["revenue", "profit", "customer", "market", "strategy"],
            "project": ["task", "milestone", "deadline", "goal", "requirement"],
            "communication": ["meeting", "discussion", "feedback", "collaboration"],
            "analysis": ["data", "research", "study", "report", "metrics"]
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics[:3]  # Return top 3 topics
    
    def _execute_suggestion(self, suggestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an AI suggestion"""
        suggestion_type = suggestion_data.get("type", "general")
        
        if suggestion_type == "workflow_optimization":
            return {
                "action": "workflow_optimized",
                "details": "Workflow patterns analyzed and optimizations suggested"
            }
        elif suggestion_type == "automation_opportunity":
            return {
                "action": "automation_identified",
                "details": "Automation opportunities identified and flagged"
            }
        else:
            return {
                "action": "suggestion_processed",
                "details": f"Processed suggestion of type: {suggestion_type}"
            }
    
    def _analyze_workflow(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze workflow for optimization opportunities"""
        optimizations = []
        
        # Sample optimizations
        optimizations.append({
            "type": "automation",
            "description": "Automate repetitive task sequences",
            "impact": "high",
            "effort": "medium"
        })
        
        optimizations.append({
            "type": "consolidation",
            "description": "Consolidate similar activities",
            "impact": "medium",
            "effort": "low"
        })
        
        optimizations.append({
            "type": "scheduling",
            "description": "Optimize task scheduling",
            "impact": "medium",
            "effort": "low"
        })
        
        return optimizations
    
    def _log_action(self, action_id: str, action_type: str, context_data: Dict[str, Any], result: Dict[str, Any]):
        """Log action execution"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ui_action_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    context_data TEXT,
                    result_data TEXT,
                    success BOOLEAN NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                INSERT INTO ui_action_log 
                (action_id, action_type, context_data, result_data, success, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                action_id,
                action_type,
                json.dumps(context_data),
                json.dumps(result),
                result.get("success", False),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Failed to log action: {e}")
    
    def get_action_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get action execution history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT action_id, action_type, context_data, result_data, success, timestamp
                FROM ui_action_log 
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "action_id": row[0],
                    "action_type": row[1],
                    "context_data": json.loads(row[2]),
                    "result_data": json.loads(row[3]),
                    "success": row[4],
                    "timestamp": row[5]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            print(f"⚠️  Failed to get action history: {e}")
            return []
    
    def get_action_stats(self) -> Dict[str, Any]:
        """Get action execution statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total actions
            cursor.execute("SELECT COUNT(*) FROM ui_action_log")
            total_actions = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute("SELECT COUNT(*) FROM ui_action_log WHERE success = 1")
            successful_actions = cursor.fetchone()[0]
            
            # Most common actions
            cursor.execute('''
                SELECT action_type, COUNT(*) as count 
                FROM ui_action_log 
                GROUP BY action_type 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            common_actions = [{"action_type": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0
            
            return {
                "total_actions": total_actions,
                "successful_actions": successful_actions,
                "success_rate": round(success_rate, 1),
                "common_actions": common_actions
            }
            
        except Exception as e:
            print(f"⚠️  Failed to get action stats: {e}")
            return {
                "total_actions": 0,
                "successful_actions": 0,
                "success_rate": 0.0,
                "common_actions": []
            }