"""
Natural Language Processing module for Workspace AI Assistant
Handles text analysis, project element extraction, and insight generation
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ProjectElement:
    """Structured project element extracted from user input"""
    vision: str = ""
    scope: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    milestones: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    priority: str = "medium"
    category: str = "general"

class NLPProcessor:
    """Natural Language Processing for workspace automation"""
    
    def __init__(self):
        self.keywords = {
            "vision": ["vision", "goal", "objective", "aim", "purpose", "mission"],
            "scope": ["scope", "includes", "covers", "encompasses", "involves"],
            "risks": ["risk", "danger", "threat", "concern", "issue", "problem"],
            "milestones": ["milestone", "target", "deadline", "phase", "step", "stage"],
            "deliverables": ["deliverable", "output", "result", "product", "artifact"],
            "dependencies": ["depends", "requires", "needs", "prerequisite", "dependency"],
            "priority": ["urgent", "high", "medium", "low", "critical", "important"]
        }
        
        self.priority_mapping = {
            "urgent": "high",
            "critical": "high",
            "important": "high",
            "high": "high",
            "medium": "medium",
            "normal": "medium",
            "low": "low"
        }
    
    def extract_project_elements(self, text: str) -> 'ProjectElement':
        """Extract structured project elements from natural language text"""
        element = ProjectElement()
        
        # Clean and normalize text
        text = self._clean_text(text)
        sentences = self._split_into_sentences(text)
        
        # Extract vision (usually the first sentence or most comprehensive statement)
        element.vision = self._extract_vision(sentences)
        
        # Extract other elements
        element.scope = self._extract_list_elements(sentences, "scope")
        element.risks = self._extract_list_elements(sentences, "risks")
        element.milestones = self._extract_list_elements(sentences, "milestones")
        element.deliverables = self._extract_list_elements(sentences, "deliverables")
        element.dependencies = self._extract_list_elements(sentences, "dependencies")
        
        # Extract priority
        element.priority = self._extract_priority(text)
        
        # Categorize based on content
        element.category = self._categorize_content(text)
        
        return element
    
    def extract_insights_from_activities(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract insights from user activities"""
        insights = {
            "patterns": [],
            "frequent_apps": [],
            "time_distribution": {},
            "productivity_score": 0.0,
            "suggestions": []
        }
        
        if not activities:
            return insights
        
        # Analyze application usage patterns
        app_usage = {}
        for activity in activities:
            app_name = activity.get("application", "Unknown")
            if app_name not in app_usage:
                app_usage[app_name] = 0
            app_usage[app_name] += 1
        
        # Get most frequently used apps
        insights["frequent_apps"] = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Analyze time distribution
        time_blocks = self._analyze_time_blocks(activities)
        insights["time_distribution"] = time_blocks
        
        # Calculate productivity score
        insights["productivity_score"] = self._calculate_productivity_score(activities)
        
        # Generate patterns
        insights["patterns"] = self._detect_activity_patterns(activities)
        
        return insights
    
    def generate_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI suggestions based on context"""
        suggestions = []
        
        # Analyze activity insights
        if "activity_insights" in context:
            activity_data = context["activity_insights"]
            for insight in activity_data:
                data = insight["data"]
                
                # Suggest workflow optimizations
                if data.get("productivity_score", 0) < 0.7:
                    suggestions.append({
                        "id": "optimize_workflow",
                        "title": "Optimize Workflow",
                        "description": "Your productivity score is below optimal. Consider organizing tasks better.",
                        "type": "workflow_optimization",
                        "priority": "medium"
                    })
                
                # Suggest automation for repeated patterns
                patterns = data.get("patterns", [])
                if len(patterns) > 2:
                    suggestions.append({
                        "id": "automate_patterns",
                        "title": "Automate Repeated Tasks",
                        "description": f"Detected {len(patterns)} repeated patterns that could be automated.",
                        "type": "automation_opportunity",
                        "priority": "high"
                    })
        
        return suggestions
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize input text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:\-()]', '', text)
        
        return text
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_vision(self, sentences: List[str]) -> str:
        """Extract the main vision/goal from sentences"""
        if not sentences:
            return ""
        
        # Look for sentences with vision keywords
        vision_sentences = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in self.keywords["vision"]):
                vision_sentences.append(sentence)
        
        if vision_sentences:
            return vision_sentences[0]
        
        # If no vision keywords found, use the first substantial sentence
        for sentence in sentences:
            if len(sentence.split()) > 5:  # At least 5 words
                return sentence
        
        return sentences[0] if sentences else ""
    
    def _extract_list_elements(self, sentences: List[str], element_type: str) -> List[str]:
        """Extract list elements (scope, risks, etc.) from sentences"""
        elements = []
        keywords = self.keywords.get(element_type, [])
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains relevant keywords
            if any(keyword in sentence_lower for keyword in keywords):
                # Extract items from lists (bullet points, numbered lists, etc.)
                items = self._extract_list_items(sentence)
                elements.extend(items)
        
        return list(set(elements))  # Remove duplicates
    
    def _extract_list_items(self, sentence: str) -> List[str]:
        """Extract individual items from a sentence that might contain lists"""
        items = []
        
        # Look for bullet points, numbers, or comma-separated items
        # Pattern for bullet points: "- item1, - item2" or "• item1, • item2"
        bullet_pattern = r'[-•*]\s*([^,-]+)'
        bullet_matches = re.findall(bullet_pattern, sentence)
        if bullet_matches:
            items.extend([match.strip() for match in bullet_matches])
        
        # Pattern for numbered lists: "1. item1, 2. item2"
        number_pattern = r'\d+\.\s*([^,\d]+)'
        number_matches = re.findall(number_pattern, sentence)
        if number_matches:
            items.extend([match.strip() for match in number_matches])
        
        # If no structured list found, try comma separation
        if not items:
            # Look for comma-separated items after keywords
            comma_items = sentence.split(',')
            if len(comma_items) > 1:
                items.extend([item.strip() for item in comma_items[1:]])
        
        # Clean up items
        cleaned_items = []
        for item in items:
            item = item.strip()
            if len(item) > 2 and not item.lower().startswith(('the', 'a', 'an')):
                cleaned_items.append(item)
        
        return cleaned_items
    
    def _extract_priority(self, text: str) -> str:
        """Extract priority level from text"""
        text_lower = text.lower()
        
        for priority_word, priority_level in self.priority_mapping.items():
            if priority_word in text_lower:
                return priority_level
        
        return "medium"  # default
    
    def _categorize_content(self, text: str) -> str:
        """Categorize content based on keywords and context"""
        text_lower = text.lower()
        
        categories = {
            "development": ["code", "software", "application", "system", "programming", "development"],
            "design": ["design", "ui", "ux", "interface", "visual", "graphic"],
            "marketing": ["marketing", "campaign", "promotion", "advertising", "brand"],
            "business": ["business", "strategy", "plan", "revenue", "profit", "market"],
            "research": ["research", "study", "analysis", "investigation", "survey"],
            "operations": ["operations", "process", "workflow", "procedure", "maintenance"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "general"
    
    def _analyze_time_blocks(self, activities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze time distribution across different periods"""
        time_blocks = {
            "morning": 0,
            "afternoon": 0,
            "evening": 0,
            "night": 0
        }
        
        for activity in activities:
            timestamp = activity.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    
                    if 6 <= hour < 12:
                        time_blocks["morning"] += 1
                    elif 12 <= hour < 17:
                        time_blocks["afternoon"] += 1
                    elif 17 <= hour < 22:
                        time_blocks["evening"] += 1
                    else:
                        time_blocks["night"] += 1
                except:
                    pass
        
        return time_blocks
    
    def _calculate_productivity_score(self, activities: List[Dict[str, Any]]) -> float:
        """Calculate productivity score based on activities"""
        if not activities:
            return 0.0
        
        productive_apps = [
            "code", "vscode", "cursor", "pycharm", "intellij", "sublime", "atom",
            "word", "excel", "powerpoint", "libreoffice", "google docs",
            "figma", "sketch", "photoshop", "illustrator",
            "slack", "teams", "zoom", "discord"
        ]
        
        total_activities = len(activities)
        productive_activities = 0
        
        for activity in activities:
            app_name = activity.get("application", "").lower()
            if any(prod_app in app_name for prod_app in productive_apps):
                productive_activities += 1
        
        return productive_activities / total_activities if total_activities > 0 else 0.0
    
    def _detect_activity_patterns(self, activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect repeated patterns in activities"""
        patterns = []
        
        # Simple pattern detection - could be enhanced with more sophisticated algorithms
        app_sequences = []
        for activity in activities:
            app_name = activity.get("application", "Unknown")
            app_sequences.append(app_name)
        
        # Look for repeated sequences of 2-3 apps
        for seq_length in [2, 3]:
            sequences = {}
            for i in range(len(app_sequences) - seq_length + 1):
                seq = tuple(app_sequences[i:i + seq_length])
                if seq not in sequences:
                    sequences[seq] = 0
                sequences[seq] += 1
            
            # Find sequences that occur more than once
            for seq, count in sequences.items():
                if count > 1:
                    patterns.append({
                        "sequence": list(seq),
                        "count": count,
                        "length": seq_length
                    })
        
        return patterns[:5]  # Return top 5 patterns