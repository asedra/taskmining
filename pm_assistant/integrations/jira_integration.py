"""
Jira Integration Module
======================

Handles Jira integration via MCP (Model Context Protocol) for project management.
"""

import json
import logging
from typing import Dict, Any, Optional
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)

class JiraIntegration:
    """Handles Jira operations via MCP protocol"""
    
    def __init__(self):
        self.mcp_configured = self._check_mcp_configuration()
        logger.info(f"Jira Integration initialized (MCP configured: {self.mcp_configured})")
    
    def _check_mcp_configuration(self) -> bool:
        """Check if MCP is properly configured for Jira"""
        try:
            # Check if .cursor/mcp.json exists and has Jira configuration
            with open('.cursor/mcp.json', 'r') as f:
                config = json.load(f)
                return any(server.get('name') == 'jira' for server in config.get('servers', []))
        except Exception:
            return False
    
    def create_epic(self, epic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Epic in Jira via MCP"""
        if not self.mcp_configured:
            return {"success": False, "error": "MCP not configured for Jira"}
        
        try:
            # In a real implementation, this would use MCP to communicate with Jira
            # For now, return a mock response
            mock_response = {
                "success": True,
                "key": f"EPIC-{hash(epic_data['summary']) % 1000}",
                "id": str(hash(epic_data['summary'])),
                "summary": epic_data['summary']
            }
            logger.info(f"Epic created: {mock_response['key']}")
            return mock_response
        except Exception as e:
            logger.error(f"Error creating epic: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Story in Jira via MCP"""
        if not self.mcp_configured:
            return {"success": False, "error": "MCP not configured for Jira"}
        
        try:
            mock_response = {
                "success": True,
                "key": f"STORY-{hash(story_data['summary']) % 1000}",
                "id": str(hash(story_data['summary'])),
                "summary": story_data['summary']
            }
            logger.info(f"Story created: {mock_response['key']}")
            return mock_response
        except Exception as e:
            logger.error(f"Error creating story: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Task in Jira via MCP"""
        if not self.mcp_configured:
            return {"success": False, "error": "MCP not configured for Jira"}
        
        try:
            mock_response = {
                "success": True,
                "key": f"TASK-{hash(task_data['summary']) % 1000}",
                "id": str(hash(task_data['summary'])),
                "summary": task_data['summary']
            }
            logger.info(f"Task created: {mock_response['key']}")
            return mock_response
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_issue_details(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get issue details from Jira"""
        if not self.mcp_configured:
            return None
        
        try:
            # Mock response for now
            return {
                "key": issue_key,
                "status": "To Do",
                "assignee": None,
                "created": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting issue details: {str(e)}")
            return None