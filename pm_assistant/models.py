"""
PM Assistant Models
==================

Data models and classes used throughout the PM Assistant system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class ProjectIdea:
    """Represents a project idea with PMI structure"""
    id: str
    summary: str
    description: str
    category: str  # vision, scope, risk, milestone, deliverable, dependency
    priority: str  # high, medium, low
    tags: List[str]
    jira_ref: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()