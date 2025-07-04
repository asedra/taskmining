"""
Jira MCP Client - Model Context Protocol integration for Jira
Handles Jira issue creation, updates, and project management following MCP methodology
"""

import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import os
import base64

@dataclass
class JiraIssue:
    """Jira issue structure following MCP methodology"""
    issue_type: str  # Epic, Story, Task
    title: str
    description: str
    milestone: str = ""
    component: str = ""
    phase: str = ""
    priority: str = "medium"
    assignee: str = ""
    labels: List[str] = field(default_factory=list)
    jira_key: str = ""
    status: str = "To Do"

@dataclass
class JiraProject:
    """Jira project structure"""
    key: str
    name: str
    project_type: str = "software"
    description: str = ""

class JiraMCPClient:
    """Jira client implementing MCP methodology for issue organization"""
    
    def __init__(self, base_url: Optional[str] = None, username: Optional[str] = None, api_token: Optional[str] = None):
        # Try to get credentials from environment variables
        self.base_url = base_url or os.getenv("JIRA_BASE_URL") or ""
        self.username = username or os.getenv("JIRA_USERNAME") or ""
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN") or ""
        
        # MCP methodology mapping
        self.mcp_hierarchy = {
            "Epic": {
                "level": "milestone",
                "parent": None,
                "children": ["Story"]
            },
            "Story": {
                "level": "component",
                "parent": "Epic",
                "children": ["Task", "Sub-task"]
            },
            "Task": {
                "level": "phase",
                "parent": "Story",
                "children": ["Sub-task"]
            },
            "Sub-task": {
                "level": "implementation",
                "parent": "Task",
                "children": []
            }
        }
        
        # Priority mapping
        self.priority_mapping = {
            "low": "Low",
            "medium": "Medium",
            "high": "High",
            "critical": "Highest"
        }
        
        # Default project key
        self.default_project_key = os.getenv("JIRA_PROJECT_KEY") or "WKSPC"
        
        # Session setup
        self.session = requests.Session()
        if self.username and self.api_token:
            self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup authentication for Jira API"""
        auth_string = f"{self.username}:{self.api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.session.headers.update({
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_connection(self) -> bool:
        """Test connection to Jira"""
        if not self.base_url or not self.username or not self.api_token:
            print("⚠️  Jira credentials not configured")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/rest/api/3/myself")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Jira connection test failed: {e}")
            return False
    
    def create_issue(self, issue: JiraIssue) -> Optional[JiraIssue]:
        """Create a Jira issue following MCP methodology"""
        if not self.test_connection():
            print("⚠️  Creating mock Jira issue (no connection)")
            return self._create_mock_issue(issue)
        
        try:
            # Prepare issue data
            issue_data = self._prepare_issue_data(issue)
            
            # Create the issue
            response = self.session.post(
                f"{self.base_url}/rest/api/3/issue",
                data=json.dumps(issue_data)
            )
            
            if response.status_code == 201:
                result = response.json()
                issue.jira_key = result.get("key", "")
                print(f"✅ Created Jira issue: {issue.jira_key}")
                return issue
            else:
                print(f"❌ Failed to create Jira issue: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating Jira issue: {e}")
            return None
    
    def _prepare_issue_data(self, issue: JiraIssue) -> Dict[str, Any]:
        """Prepare issue data for Jira API"""
        # Map issue type to Jira issue type
        jira_issue_type = self._map_issue_type(issue.issue_type)
        
        # Map priority
        jira_priority = self.priority_mapping.get(issue.priority, "Medium")
        
        # Prepare fields
        fields = {
            "project": {"key": self.default_project_key},
            "summary": issue.title,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": issue.description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"name": jira_issue_type},
            "priority": {"name": jira_priority}
        }
        
        # Add labels if any
        if issue.labels:
            fields["labels"] = issue.labels
        
        # Add MCP-specific custom fields
        if issue.milestone:
            fields["customfield_milestone"] = issue.milestone
        if issue.component:
            fields["customfield_component"] = issue.component
        if issue.phase:
            fields["customfield_phase"] = issue.phase
        
        return {"fields": fields}
    
    def _map_issue_type(self, issue_type: str) -> str:
        """Map internal issue type to Jira issue type"""
        mapping = {
            "Epic": "Epic",
            "Story": "Story",
            "Task": "Task",
            "Sub-task": "Sub-task"
        }
        return mapping.get(issue_type, "Task")
    
    def _create_mock_issue(self, issue: JiraIssue) -> JiraIssue:
        """Create a mock issue for testing without Jira connection"""
        issue.jira_key = f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        issue.status = "Created (Mock)"
        return issue
    
    def create_mcp_structure(self, project_elements: List[Dict[str, Any]]) -> List[JiraIssue]:
        """Create MCP-structured issues from project elements"""
        created_issues = []
        
        for element in project_elements:
            # Create Epic for vision
            if element.get("vision"):
                epic = JiraIssue(
                    issue_type="Epic",
                    title=f"Epic: {element['vision'][:50]}...",
                    description=element["vision"],
                    priority=element.get("priority", "medium"),
                    milestone=element.get("category", "general")
                )
                created_epic = self.create_issue(epic)
                if created_epic:
                    created_issues.append(created_epic)
            
            # Create Stories for milestones
            for milestone in element.get("milestones", []):
                story = JiraIssue(
                    issue_type="Story",
                    title=f"Story: {milestone}",
                    description=f"Milestone: {milestone}",
                    milestone=milestone,
                    priority=element.get("priority", "medium")
                )
                created_story = self.create_issue(story)
                if created_story:
                    created_issues.append(created_story)
            
            # Create Tasks for deliverables
            for deliverable in element.get("deliverables", []):
                task = JiraIssue(
                    issue_type="Task",
                    title=f"Task: {deliverable}",
                    description=f"Deliverable: {deliverable}",
                    component=deliverable,
                    priority=element.get("priority", "medium")
                )
                created_task = self.create_issue(task)
                if created_task:
                    created_issues.append(created_task)
        
        return created_issues
    
    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """Update an existing Jira issue"""
        if not self.test_connection():
            print(f"⚠️  Mock update for issue {issue_key}")
            return True
        
        try:
            response = self.session.put(
                f"{self.base_url}/rest/api/3/issue/{issue_key}",
                data=json.dumps({"fields": fields})
            )
            
            if response.status_code == 204:
                print(f"✅ Updated Jira issue: {issue_key}")
                return True
            else:
                print(f"❌ Failed to update Jira issue: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating Jira issue: {e}")
            return False
    
    def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get a Jira issue by key"""
        if not self.test_connection():
            return None
        
        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/3/issue/{issue_key}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get Jira issue: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting Jira issue: {e}")
            return None
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for issues using JQL"""
        if not self.test_connection():
            return []
        
        try:
            response = self.session.post(
                f"{self.base_url}/rest/api/3/search",
                data=json.dumps({
                    "jql": jql,
                    "maxResults": max_results
                })
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("issues", [])
            else:
                print(f"❌ Failed to search Jira issues: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching Jira issues: {e}")
            return []
    
    def get_project_info(self, project_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get project information"""
        project_key = project_key or self.default_project_key
        
        if not self.test_connection():
            return {
                "key": project_key,
                "name": f"Mock Project {project_key}",
                "projectTypeKey": "software"
            }
        
        try:
            response = self.session.get(
                f"{self.base_url}/rest/api/3/project/{project_key}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get project info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting project info: {e}")
            return None
    
    def organize_by_mcp(self, issues: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Organize issues by MCP methodology (Milestone → Component → Phase)"""
        organized = {
            "milestones": {},
            "components": {},
            "phases": {}
        }
        
        for issue in issues:
            fields = issue.get("fields", {})
            issue_type = fields.get("issuetype", {}).get("name", "Task")
            
            # Organize by MCP hierarchy
            if issue_type == "Epic":
                milestone = fields.get("customfield_milestone", "Uncategorized")
                if milestone not in organized["milestones"]:
                    organized["milestones"][milestone] = []
                organized["milestones"][milestone].append(issue)
            
            elif issue_type == "Story":
                component = fields.get("customfield_component", "Uncategorized")
                if component not in organized["components"]:
                    organized["components"][component] = []
                organized["components"][component].append(issue)
            
            elif issue_type in ["Task", "Sub-task"]:
                phase = fields.get("customfield_phase", "Implementation")
                if phase not in organized["phases"]:
                    organized["phases"][phase] = []
                organized["phases"][phase].append(issue)
        
        return organized
    
    def get_mcp_dashboard(self) -> Dict[str, Any]:
        """Get MCP-organized dashboard data"""
        if not self.test_connection():
            return {
                "status": "offline",
                "message": "Jira connection not available",
                "mock_data": True
            }
        
        # Search for all issues in the project
        jql = f"project = {self.default_project_key} ORDER BY created DESC"
        issues = self.search_issues(jql, max_results=100)
        
        # Organize by MCP
        organized = self.organize_by_mcp(issues)
        
        # Calculate stats
        stats = {
            "total_issues": len(issues),
            "epics": len(organized["milestones"]),
            "stories": len(organized["components"]),
            "tasks": len(organized["phases"])
        }
        
        return {
            "status": "online",
            "stats": stats,
            "organized": organized,
            "project_key": self.default_project_key
        }