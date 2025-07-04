"""
PM Assistant: MCP-Integrated Project Management Agent
=====================================================

A Project Management Assistant AI with PMI and PMP capabilities that integrates
with the existing Task Mining system and provides Jira synchronization via MCP.

Author: user
Date: 2025-07-04
Tags: #project #arketec #pmi #cursor #jira #mcp #ai-assistant
"""

__version__ = "1.0.0"
__author__ = "user"

from .core.pm_assistant import PMAssistant
from .core.project_manager import ProjectManager
from .core.memory_manager import MemoryManager
from .integrations.jira_integration import JiraIntegration
from .utils.pmi_utils import PMIUtils
from .models import ProjectIdea

__all__ = [
    'PMAssistant',
    'ProjectManager', 
    'MemoryManager',
    'JiraIntegration',
    'PMIUtils',
    'ProjectIdea'
]