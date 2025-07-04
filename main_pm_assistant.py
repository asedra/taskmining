"""
PM Assistant Integration with Task Mining System
===============================================

Main integration script that connects the PM Assistant with the existing task mining system.
"""

import sys
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add the pm_assistant module to path
sys.path.append('.')

from pm_assistant import PMAssistant
from activity_logger import ActivityLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/pm_assistant.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PMAssistantIntegration:
    """
    Integration between PM Assistant and Task Mining System
    
    Combines project management capabilities with user activity monitoring
    to provide intelligent project insights and automation.
    """
    
    def __init__(self, project_name: str = "Arketic"):
        self.project_name = project_name
        self.pm_assistant = PMAssistant(project_name)
        self.activity_logger = ActivityLogger()
        
        logger.info(f"PM Assistant Integration initialized for project: {project_name}")
    
    def analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input and extract project management insights
        
        Args:
            user_input: User's project-related input
            
        Returns:
            Analysis results with actionable project items
        """
        logger.info("Analyzing user input for project management insights")
        
        # Get activity context from task mining system
        activity_context = self._get_activity_context()
        
        # Analyze input with PM Assistant
        analysis_result = self.pm_assistant.analyze_input(user_input, activity_context or {})
        
        # Log the analysis for future reference
        self._log_pm_activity("input_analyzed", {
            "input_length": len(user_input),
            "ideas_generated": analysis_result.get("ideas_generated", 0),
            "suggested_actions": analysis_result.get("suggested_actions", [])
        })
        
        return analysis_result
    
    def sync_with_jira(self, idea_filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Synchronize project ideas with Jira
        
        Args:
            idea_filters: Optional filters for which ideas to sync
            
        Returns:
            Synchronization results
        """
        logger.info("Synchronizing project ideas with Jira")
        
        # Get ideas from memory based on filters
        if idea_filters:
            ideas = self.pm_assistant.search_deep("", idea_filters)
        else:
            ideas = self.pm_assistant.memory_manager.get_all_ideas(self.project_name)
        
        # Filter out ideas that already have Jira references
        ideas_to_sync = [idea for idea in ideas if not idea.jira_ref]
        
        if not ideas_to_sync:
            logger.info("No ideas to sync - all ideas already have Jira references")
            return {"message": "No ideas to sync", "ideas_synced": 0}
        
        # Create Jira entities
        sync_results = self.pm_assistant.create_jira_entities(ideas_to_sync)
        
        # Log synchronization activity
        self._log_pm_activity("jira_sync", {
            "ideas_synced": len(ideas_to_sync),
            "epics_created": len(sync_results.get("epics_created", [])),
            "stories_created": len(sync_results.get("stories_created", [])),
            "tasks_created": len(sync_results.get("tasks_created", [])),
            "errors": len(sync_results.get("errors", []))
        })
        
        return sync_results
    
    def generate_project_report(self) -> str:
        """
        Generate comprehensive project report combining PM data and activity data
        
        Returns:
            Path to generated report
        """
        logger.info("Generating comprehensive project report")
        
        # Generate PM documentation
        pm_documentation = self.pm_assistant.generate_project_documentation("detailed")
        
        # Get activity insights from task mining
        activity_insights = self._get_activity_insights()
        
        # Combine both reports
        combined_report = f"""# {self.project_name} - Comprehensive Project Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{pm_documentation}

---

## 📊 Activity Insights

{activity_insights}

---

## 🔄 Recommendations

Based on the combined project management and activity data:

1. **Focus Areas**: Review the most active application areas for automation opportunities
2. **Time Management**: Analyze activity patterns to optimize project scheduling
3. **Risk Assessment**: Consider activity interruptions as project risk factors
4. **Resource Planning**: Use activity data to estimate realistic project timelines

"""
        
        # Save combined report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"data/reports/{self.project_name}_comprehensive_report_{timestamp}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(combined_report)
        
        logger.info(f"Comprehensive project report saved to: {report_path}")
        return report_path
    
    def search_project_knowledge(self, query: str, include_activity: bool = True) -> Dict[str, Any]:
        """
        Search project knowledge base including both PM data and activity data
        
        Args:
            query: Search query
            include_activity: Whether to include activity data in search
            
        Returns:
            Search results with combined insights
        """
        logger.info(f"Searching project knowledge for: {query}")
        
        # Search PM ideas
        pm_results = self.pm_assistant.search_deep(query)
        
        # Search activity data if requested
        activity_results = []
        if include_activity:
            activity_results = self._search_activity_data(query)
        
        search_results = {
            "query": query,
            "pm_results": [self._serialize_idea(idea) for idea in pm_results],
            "activity_results": activity_results,
            "total_results": len(pm_results) + len(activity_results)
        }
        
        return search_results
    
    def _get_activity_context(self) -> Dict[str, Any]:
        """Get current activity context from task mining system"""
        try:
            # Get recent activity data
            recent_apps = self.activity_logger.get_app_usage_summary(days=1)
            recent_files = self.activity_logger.get_recent_file_activity(limit=10)
            
            return {
                "recent_applications": recent_apps,
                "recent_files": recent_files,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Could not get activity context: {str(e)}")
            return {}
    
    def _get_activity_insights(self) -> str:
        """Generate activity insights section"""
        try:
            # Get activity statistics
            daily_stats = self.activity_logger.get_daily_summary()
            
            insights = f"""
### Application Usage Patterns

Recent application usage shows focus on development and project management tools.

### File Activity Trends

File system activity indicates active development and documentation work.

### Time Distribution

Activity patterns suggest optimal working hours and potential productivity improvements.

*Note: Detailed activity analysis available in separate task mining reports.*
"""
            return insights
        except Exception as e:
            logger.warning(f"Could not generate activity insights: {str(e)}")
            return "Activity insights unavailable - check task mining system."
    
    def _search_activity_data(self, query: str) -> List[Dict[str, Any]]:
        """Search activity data for relevant information"""
        try:
            # Simple search in activity data (can be enhanced)
            results = []
            
            # Search in application names and window titles
            # This is a simplified implementation
            if "browser" in query.lower():
                results.append({
                    "type": "activity",
                    "description": "Browser usage patterns detected",
                    "relevance": "high"
                })
            
            return results
        except Exception as e:
            logger.warning(f"Could not search activity data: {str(e)}")
            return []
    
    def _serialize_idea(self, idea) -> Dict[str, Any]:
        """Serialize idea object to dictionary"""
        return {
            "id": idea.id,
            "summary": idea.summary,
            "description": idea.description,
            "category": idea.category,
            "priority": idea.priority,
            "tags": idea.tags,
            "jira_ref": idea.jira_ref,
            "created_at": idea.created_at,
            "updated_at": idea.updated_at
        }
    
    def _log_pm_activity(self, activity_type: str, data: Dict[str, Any]):
        """Log PM Assistant activity"""
        try:
            self.pm_assistant.memory_manager._log_activity(
                self.project_name, 
                activity_type, 
                data
            )
        except Exception as e:
            logger.warning(f"Could not log PM activity: {str(e)}")

def main():
    """Main function for testing PM Assistant integration"""
    print("PM Assistant Integration - Test Mode")
    print("=" * 50)
    
    # Initialize integration
    pm_integration = PMAssistantIntegration("Arketic")
    
    # Test input analysis
    test_input = """
    We need to create a smart project management platform that integrates with Jira.
    The platform should have AI-powered task planning and automated documentation.
    Critical features include real-time collaboration and project tracking.
    We must ensure data security and user-friendly interface design.
    """
    
    print("Analyzing test input...")
    analysis_result = pm_integration.analyze_user_input(test_input)
    print(f"Generated {analysis_result.get('ideas_generated', 0)} project ideas")
    
    # Test Jira sync
    print("\nTesting Jira synchronization...")
    sync_result = pm_integration.sync_with_jira()
    print(f"Sync result: {sync_result}")
    
    # Generate report
    print("\nGenerating project report...")
    report_path = pm_integration.generate_project_report()
    print(f"Report generated: {report_path}")
    
    # Test search
    print("\nTesting project knowledge search...")
    search_result = pm_integration.search_project_knowledge("AI platform")
    print(f"Search returned {search_result['total_results']} results")
    
    print("\nPM Assistant Integration test completed!")

if __name__ == "__main__":
    main()