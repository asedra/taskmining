"""
PM Assistant Core Module
========================

Main PM Assistant class implementing PMI/PMP methodologies with MCP integration.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from .memory_manager import MemoryManager
from .project_manager import ProjectManager
from ..integrations.jira_integration import JiraIntegration
from ..utils.pmi_utils import PMIUtils
from ..models import ProjectIdea

logger = logging.getLogger(__name__)

class PMAssistant:
    """
    PM Assistant: MCP-Integrated Project Management Agent
    
    Provides project management capabilities with PMI/PMP methodologies,
    Jira integration via MCP, and persistent memory management.
    """
    
    def __init__(self, project_name: str = "Default Project"):
        self.project_name = project_name
        self.memory_manager = MemoryManager()
        self.project_manager = ProjectManager(project_name)
        self.jira_integration = JiraIntegration()
        self.pmi_utils = PMIUtils()
        
        # Load existing project data
        self._load_project_context()
        
        logger.info(f"PM Assistant initialized for project: {project_name}")
    
    def analyze_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user input and extract actionable project components
        
        Args:
            user_input: User's input text (Turkish/English hybrid supported)
            context: Additional context information
            
        Returns:
            Structured analysis with PMI components
        """
        logger.info("Analyzing user input for project components")
        
        # Extract core actionable items
        actionable_items = self.pmi_utils.extract_actionable_items(user_input)
        
        # Categorize into PMI components
        pmi_components = self.pmi_utils.categorize_pmi_components(actionable_items)
        
        # Generate project ideas
        ideas = []
        for component_type, items in pmi_components.items():
            for item in items:
                idea = ProjectIdea(
                    id=self._generate_idea_id(),
                    summary=item.get('summary', ''),
                    description=item.get('description', ''),
                    category=component_type,
                    priority=item.get('priority', 'medium'),
                    tags=item.get('tags', [])
                )
                ideas.append(idea)
        
        # Store in memory
        for idea in ideas:
            self.memory_manager.store_idea(idea)
        
        # Prepare analysis result
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'input_text': user_input,
            'ideas_generated': len(ideas),
            'pmi_components': pmi_components,
            'suggested_actions': self._generate_suggested_actions(ideas),
            'jira_sync_plan': self._plan_jira_sync(ideas)
        }
        
        logger.info(f"Analysis complete: {len(ideas)} ideas generated")
        return analysis_result
    
    def create_jira_entities(self, ideas: List[ProjectIdea]) -> Dict[str, Any]:
        """
        Create Jira entities (Epics, Stories, Tasks) based on project ideas
        
        Args:
            ideas: List of project ideas to convert to Jira entities
            
        Returns:
            Results of Jira entity creation
        """
        logger.info(f"Creating Jira entities for {len(ideas)} ideas")
        
        results = {
            'epics_created': [],
            'stories_created': [],
            'tasks_created': [],
            'errors': []
        }
        
        # Group ideas by category for MCP logic
        epic_ideas = [idea for idea in ideas if idea.category in ['vision', 'scope']]
        story_ideas = [idea for idea in ideas if idea.category in ['deliverable', 'milestone']]
        task_ideas = [idea for idea in ideas if idea.category in ['dependency', 'risk']]
        
        try:
            # Create Epics (Vision-level)
            for idea in epic_ideas:
                epic_data = {
                    'summary': idea.summary,
                    'description': idea.description,
                    'labels': idea.tags
                }
                epic_result = self.jira_integration.create_epic(epic_data)
                if epic_result.get('success'):
                    idea.jira_ref = epic_result['key']
                    results['epics_created'].append(epic_result)
                    self.memory_manager.update_idea(idea)
                else:
                    results['errors'].append(f"Epic creation failed: {epic_result.get('error')}")
            
            # Create Stories (User-focused requirements)
            for idea in story_ideas:
                story_data = {
                    'summary': idea.summary,
                    'description': idea.description,
                    'labels': idea.tags,
                    'epic_link': self._find_related_epic(idea, results['epics_created'])
                }
                story_result = self.jira_integration.create_story(story_data)
                if story_result.get('success'):
                    idea.jira_ref = story_result['key']
                    results['stories_created'].append(story_result)
                    self.memory_manager.update_idea(idea)
                else:
                    results['errors'].append(f"Story creation failed: {story_result.get('error')}")
            
            # Create Tasks (Actionable work units)
            for idea in task_ideas:
                task_data = {
                    'summary': idea.summary,
                    'description': idea.description,
                    'labels': idea.tags,
                    'parent_story': self._find_related_story(idea, results['stories_created'])
                }
                task_result = self.jira_integration.create_task(task_data)
                if task_result.get('success'):
                    idea.jira_ref = task_result['key']
                    results['tasks_created'].append(task_result)
                    self.memory_manager.update_idea(idea)
                else:
                    results['errors'].append(f"Task creation failed: {task_result.get('error')}")
        
        except Exception as e:
            logger.error(f"Error creating Jira entities: {str(e)}")
            results['errors'].append(f"General error: {str(e)}")
        
        logger.info(f"Jira entity creation complete: {len(results['epics_created'])} epics, "
                   f"{len(results['stories_created'])} stories, {len(results['tasks_created'])} tasks")
        
        return results
    
    def search_deep(self, query: str, filters: Dict[str, Any] = None) -> List[ProjectIdea]:
        """
        Perform deep search across project memory using semantic similarity
        
        Args:
            query: Search query
            filters: Optional filters (category, tags, date_range)
            
        Returns:
            List of matching project ideas
        """
        logger.info(f"Performing deep search for: {query}")
        
        results = self.memory_manager.search_ideas(query, filters)
        
        # Enhance results with contextual information
        enhanced_results = []
        for idea in results:
            enhanced_idea = idea
            # Add related Jira information if available
            if idea.jira_ref:
                jira_info = self.jira_integration.get_issue_details(idea.jira_ref)
                enhanced_idea.jira_info = jira_info
            enhanced_results.append(enhanced_idea)
        
        logger.info(f"Deep search returned {len(enhanced_results)} results")
        return enhanced_results
    
    def generate_project_documentation(self, template: str = "standard") -> str:
        """
        Generate project documentation based on collected ideas and PMI structure
        
        Args:
            template: Documentation template type (standard, detailed, executive)
            
        Returns:
            Generated markdown documentation
        """
        logger.info(f"Generating project documentation with template: {template}")
        
        # Get all project ideas
        all_ideas = self.memory_manager.get_all_ideas()
        
        # Group by PMI categories
        categorized_ideas = {}
        for idea in all_ideas:
            if idea.category not in categorized_ideas:
                categorized_ideas[idea.category] = []
            categorized_ideas[idea.category].append(idea)
        
        # Generate documentation using PMI structure
        documentation = self.pmi_utils.generate_documentation(
            project_name=self.project_name,
            categorized_ideas=categorized_ideas,
            template=template
        )
        
        # Save documentation
        doc_path = f"data/reports/{self.project_name}_documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self.project_manager.save_documentation(documentation, doc_path)
        
        logger.info(f"Project documentation generated and saved to: {doc_path}")
        return documentation
    
    def export_project_data(self, format_type: str = "json") -> str:
        """
        Export all project data in specified format
        
        Args:
            format_type: Export format (json, csv, markdown)
            
        Returns:
            Path to exported file
        """
        logger.info(f"Exporting project data in {format_type} format")
        
        all_ideas = self.memory_manager.get_all_ideas()
        export_path = self.project_manager.export_data(all_ideas, format_type)
        
        logger.info(f"Project data exported to: {export_path}")
        return export_path
    
    def _load_project_context(self):
        """Load existing project context from memory"""
        context = self.memory_manager.get_project_context(self.project_name)
        if context:
            logger.info(f"Loaded existing project context for: {self.project_name}")
        else:
            logger.info(f"No existing context found, starting fresh project: {self.project_name}")
    
    def _generate_idea_id(self) -> str:
        """Generate unique ID for project idea"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.project_name.lower().replace(' ', '_')}_{timestamp}"
    
    def _generate_suggested_actions(self, ideas: List[ProjectIdea]) -> List[str]:
        """Generate suggested actions based on ideas"""
        actions = []
        
        if any(idea.category == 'vision' for idea in ideas):
            actions.append("Create project charter and vision statement")
        
        if any(idea.category == 'scope' for idea in ideas):
            actions.append("Define detailed project scope and boundaries")
        
        if any(idea.category == 'risk' for idea in ideas):
            actions.append("Develop risk mitigation strategies")
        
        if any(idea.category == 'milestone' for idea in ideas):
            actions.append("Create project timeline with milestones")
        
        return actions
    
    def _plan_jira_sync(self, ideas: List[ProjectIdea]) -> Dict[str, int]:
        """Plan Jira synchronization based on ideas"""
        plan = {
            'epics_to_create': len([i for i in ideas if i.category in ['vision', 'scope']]),
            'stories_to_create': len([i for i in ideas if i.category in ['deliverable', 'milestone']]),
            'tasks_to_create': len([i for i in ideas if i.category in ['dependency', 'risk']])
        }
        return plan
    
    def _find_related_epic(self, idea: ProjectIdea, created_epics: List[Dict]) -> Optional[str]:
        """Find related epic for story linking"""
        # Simple logic: link to first epic or None
        return created_epics[0]['key'] if created_epics else None
    
    def _find_related_story(self, idea: ProjectIdea, created_stories: List[Dict]) -> Optional[str]:
        """Find related story for task linking"""
        # Simple logic: link to first story or None
        return created_stories[0]['key'] if created_stories else None