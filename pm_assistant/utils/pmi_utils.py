"""
PMI Utilities Module
===================

Utilities for PMI/PMP methodologies, text analysis, and documentation generation.
"""

import re
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PMIUtils:
    """Utilities for PMI/PMP project management methodologies"""
    
    def __init__(self):
        self.pmi_keywords = {
            'vision': ['vision', 'goal', 'objective', 'purpose', 'mission', 'aim'],
            'scope': ['scope', 'boundary', 'deliverable', 'requirement', 'feature'],
            'risk': ['risk', 'threat', 'issue', 'problem', 'challenge', 'concern'],
            'milestone': ['milestone', 'deadline', 'phase', 'checkpoint', 'target'],
            'deliverable': ['deliverable', 'output', 'product', 'result', 'outcome'],
            'dependency': ['dependency', 'prerequisite', 'requirement', 'needs', 'depends']
        }
        
        self.priority_keywords = {
            'high': ['urgent', 'critical', 'important', 'priority', 'asap'],
            'medium': ['normal', 'standard', 'regular', 'moderate'],
            'low': ['nice to have', 'future', 'optional', 'later', 'low priority']
        }
    
    def extract_actionable_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract actionable items from user input"""
        logger.info("Extracting actionable items from text")
        
        # Split text into sentences
        sentences = re.split(r'[.!?]\s+', text)
        
        items = []
        for sentence in sentences:
            if len(sentence.strip()) < 10:  # Skip very short sentences
                continue
            
            # Extract potential action items
            if any(keyword in sentence.lower() for keyword in ['need', 'should', 'must', 'will', 'plan', 'create', 'develop']):
                priority = self._determine_priority(sentence)
                
                item = {
                    'summary': sentence.strip()[:100],  # Limit summary length
                    'description': sentence.strip(),
                    'priority': priority,
                    'tags': self._extract_tags(sentence)
                }
                items.append(item)
        
        logger.info(f"Extracted {len(items)} actionable items")
        return items
    
    def categorize_pmi_components(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize items into PMI components"""
        logger.info("Categorizing items into PMI components")
        
        categorized = {category: [] for category in self.pmi_keywords.keys()}
        
        for item in items:
            text = f"{item['summary']} {item['description']}".lower()
            
            # Find best matching category
            best_category = 'scope'  # default category
            best_score = 0
            
            for category, keywords in self.pmi_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > best_score:
                    best_score = score
                    best_category = category
            
            categorized[best_category].append(item)
        
        # Log categorization results
        for category, cat_items in categorized.items():
            if cat_items:
                logger.info(f"Category '{category}': {len(cat_items)} items")
        
        return categorized
    
    def generate_documentation(self, project_name: str, categorized_ideas: Dict[str, List[Any]], template: str = "standard") -> str:
        """Generate project documentation using PMI structure"""
        logger.info(f"Generating {template} documentation for project: {project_name}")
        
        doc = f"""# {project_name} - Project Documentation

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Template:** {template.title()}

---

## 🎯 Project Vision
"""
        
        if 'vision' in categorized_ideas and categorized_ideas['vision']:
            for idea in categorized_ideas['vision']:
                doc += f"- {self._get_idea_summary(idea)}\n"
        else:
            doc += "- *No vision items defined yet*\n"
        
        doc += """
## 📋 Project Scope
"""
        
        if 'scope' in categorized_ideas and categorized_ideas['scope']:
            for idea in categorized_ideas['scope']:
                doc += f"- {self._get_idea_summary(idea)}\n"
        else:
            doc += "- *No scope items defined yet*\n"
        
        doc += """
## 🚩 Risks & Issues
"""
        
        if 'risk' in categorized_ideas and categorized_ideas['risk']:
            for idea in categorized_ideas['risk']:
                doc += f"- **{idea.priority if hasattr(idea, 'priority') else 'Medium'}**: {self._get_idea_summary(idea)}\n"
        else:
            doc += "- *No risks identified yet*\n"
        
        doc += """
## 🏁 Milestones
"""
        
        if 'milestone' in categorized_ideas and categorized_ideas['milestone']:
            for idea in categorized_ideas['milestone']:
                doc += f"- {self._get_idea_summary(idea)}\n"
        else:
            doc += "- *No milestones defined yet*\n"
        
        doc += """
## 📦 Deliverables
"""
        
        if 'deliverable' in categorized_ideas and categorized_ideas['deliverable']:
            for idea in categorized_ideas['deliverable']:
                doc += f"- {self._get_idea_summary(idea)}\n"
        else:
            doc += "- *No deliverables defined yet*\n"
        
        doc += """
## 🔗 Dependencies
"""
        
        if 'dependency' in categorized_ideas and categorized_ideas['dependency']:
            for idea in categorized_ideas['dependency']:
                doc += f"- {self._get_idea_summary(idea)}\n"
        else:
            doc += "- *No dependencies identified yet*\n"
        
        if template == "detailed":
            doc += self._add_detailed_sections(categorized_ideas)
        
        return doc
    
    def _determine_priority(self, text: str) -> str:
        """Determine priority based on text content"""
        text_lower = text.lower()
        
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return priority
        
        return 'medium'  # default priority
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from text"""
        # Simple tag extraction based on common project management terms
        tags = []
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['ui', 'ux', 'interface', 'design']):
            tags.append('ui-ux')
        
        if any(word in text_lower for word in ['api', 'backend', 'server', 'database']):
            tags.append('backend')
        
        if any(word in text_lower for word in ['test', 'testing', 'qa', 'quality']):
            tags.append('testing')
        
        if any(word in text_lower for word in ['doc', 'documentation', 'manual']):
            tags.append('documentation')
        
        return tags
    
    def _get_idea_summary(self, idea: Any) -> str:
        """Get summary from idea object"""
        if hasattr(idea, 'summary'):
            return idea.summary
        elif hasattr(idea, 'get'):
            return idea.get('summary', str(idea))
        else:
            return str(idea)
    
    def _add_detailed_sections(self, categorized_ideas: Dict[str, List[Any]]) -> str:
        """Add detailed sections for detailed template"""
        detailed_content = """

## 📊 Project Statistics

"""
        
        total_items = sum(len(items) for items in categorized_ideas.values())
        detailed_content += f"- **Total Items**: {total_items}\n"
        
        for category, items in categorized_ideas.items():
            detailed_content += f"- **{category.title()}**: {len(items)} items\n"
        
        detailed_content += """

## 🔄 Implementation Plan

Based on the categorized items, the recommended implementation approach is:

1. **Phase 1: Foundation** - Establish vision and scope
2. **Phase 2: Planning** - Define milestones and dependencies  
3. **Phase 3: Development** - Create deliverables
4. **Phase 4: Risk Management** - Address identified risks

"""
        
        return detailed_content