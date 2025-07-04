"""
Project Manager Module
=====================

Handles project-level operations, documentation generation, and data export.
"""

import json
import csv
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ProjectManager:
    """Manages project-level operations and documentation"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.reports_dir = Path("data/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Project Manager initialized for: {project_name}")
    
    def save_documentation(self, content: str, file_path: str) -> bool:
        """Save documentation to file"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error saving documentation: {str(e)}")
            return False
    
    def export_data(self, ideas: List[Any], format_type: str) -> str:
        """Export project data in specified format"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type == "json":
            file_path = self.reports_dir / f"{self.project_name}_export_{timestamp}.json"
            data = [idea.__dict__ if hasattr(idea, '__dict__') else str(idea) for idea in ideas]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format_type == "csv":
            file_path = self.reports_dir / f"{self.project_name}_export_{timestamp}.csv"
            if ideas:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['id', 'summary', 'category', 'priority'])
                    writer.writeheader()
                    for idea in ideas:
                        if hasattr(idea, '__dict__'):
                            writer.writerow(idea.__dict__)
        
        return str(file_path)