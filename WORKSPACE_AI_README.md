# 🚀 Workspace AI Assistant

**Advanced AI automation assistant designed for the Cursor AI environment, combining Max Mode capabilities with persistent Background Agent functionality.**

## 🎯 Overview

The Workspace AI Assistant is a comprehensive automation system that integrates task mining, natural language processing, project management, and browser automation to create an intelligent workspace companion. It operates continuously in the background, analyzing your work patterns and providing intelligent assistance through quick actions and automated workflows.

## ✨ Key Features

### 🧠 **AI-Powered Analysis**
- **Background Monitoring**: Continuously monitors user activities, decisions, and work patterns
- **Natural Language Processing**: Extracts structured project elements from user inputs
- **Context-Aware Suggestions**: Provides intelligent suggestions based on current work context
- **Pattern Recognition**: Identifies repeated workflows and automation opportunities

### 🎯 **Jira Integration with MCP Methodology**
- **Model Context Protocol (MCP)**: Organizes issues using Milestone → Component → Phase hierarchy
- **Automated Issue Creation**: Converts natural language inputs into structured Jira issues
- **Epic/Story/Task Management**: Automatically creates appropriate issue types based on content
- **Smart Prioritization**: Analyzes content to determine issue priority and categorization

### 🌐 **Chrome Automation with Ray**
- **Distributed Computing**: Uses Ray for scalable browser automation
- **Jira Web Integration**: Automated login and issue creation through web interface
- **Credential Management**: Secure storage and reuse of login credentials
- **Screenshot Capture**: Automated documentation of actions and results

### ⚡ **Quick Action System**
- **Contextual Actions**: Dynamic action buttons based on current context
- **One-Click Operations**: "Create Jira Task", "Summarize", "Analyze Impact"
- **Custom Workflows**: User-defined automation sequences
- **Usage Analytics**: Tracks and optimizes frequently used actions

### 📊 **Advanced Analytics**
- **Activity Insights**: Detailed analysis of work patterns and productivity
- **Workflow Optimization**: Identifies bottlenecks and improvement opportunities
- **Time Tracking**: Automatic logging of application usage and task durations
- **Performance Metrics**: Success rates, completion times, and efficiency scores

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for automation features)
- Cursor AI environment
- Optional: Jira account and API credentials

### 1. Clone and Setup
```bash
git clone <repository-url>
cd workspace-ai-assistant
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the project root:
```env
# Jira Configuration (Optional)
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJ

# Chrome Automation (Optional)
CHROME_HEADLESS=false
CHROME_DOWNLOAD_PATH=/path/to/downloads

# AI Assistant Settings
WORKSPACE_AI_DB_PATH=data/workspace_ai.db
MONITORING_INTERVAL=60
DEBUG_MODE=false
```

### 3. Initial Setup
```bash
# Create required directories
mkdir -p data/reports data/screenshots

# Initialize the database
python -c "from workspace_ai_assistant import workspace_ai; workspace_ai._init_workspace_db()"

# Test the installation
python workspace_ai_main.py
```

## 🚀 Usage Guide

### Starting the Assistant
```bash
# Full interactive mode
python workspace_ai_main.py

# Background mode only
python -c "from workspace_ai_assistant import workspace_ai; workspace_ai.start_background_monitoring()"
```

### Natural Language Processing
The assistant can process natural language inputs and extract structured project elements:

```python
from workspace_ai_assistant import workspace_ai

# Process project description
text = """
Vision: Create a customer feedback analysis system
Scope: Data collection, sentiment analysis, reporting dashboard
Risks: Data privacy compliance, API rate limits
Milestones: MVP by Q2, Beta testing Q3, Production Q4
Deliverables: Web dashboard, API endpoints, Mobile app
Dependencies: Machine learning models, Cloud infrastructure
Priority: High
"""

element = workspace_ai.process_natural_language_input(text)
print(f"Vision: {element.vision}")
print(f"Scope: {element.scope}")
print(f"Priority: {element.priority}")
```

### Jira Integration
Automatically create structured Jira issues using MCP methodology:

```python
# Create Jira issues from project element
jira_issues = workspace_ai.create_jira_issues(element)

# Manual issue creation
from jira_mcp_client import JiraIssue
issue = JiraIssue(
    issue_type="Story",
    title="Implement user authentication",
    description="Add secure login functionality",
    priority="high",
    labels=["security", "backend"]
)
created_issue = workspace_ai.jira_client.create_issue(issue)
```

### Chrome Automation
Automate browser interactions for Jira and other web applications:

```python
# Login to Jira
workspace_ai.chrome_automation.execute_action("login_jira", {
    "url": "https://your-jira-instance.com",
    "username": "your-username",
    "password": "your-password"
})

# Create issue through web interface
workspace_ai.chrome_automation.execute_action("create_jira_issue", {
    "issue_type": "Task",
    "title": "Fix login bug",
    "description": "Users cannot login with special characters"
})
```

### Quick Actions
Execute quick actions programmatically:

```python
# Summarize selected text
result = workspace_ai.execute_quick_action("summarize_content", {
    "selected_text": "Long text content to summarize...",
    "action_type": "summarize"
})

# Analyze impact
result = workspace_ai.execute_quick_action("analyze_impact", {
    "selected_text": "Proposed change description...",
    "analysis_type": "impact"
})
```

## 📚 API Reference

### WorkspaceAIAssistant Class

#### Core Methods
- `start_background_monitoring()`: Start continuous monitoring
- `stop_background_monitoring()`: Stop monitoring gracefully
- `process_natural_language_input(text)`: Extract project elements from text
- `create_jira_issues(element)`: Create Jira issues from project element
- `get_quick_actions(context)`: Get available quick actions
- `execute_quick_action(action_id, context)`: Execute a quick action

#### Context Management
- `_get_current_context()`: Get current user context
- `_store_user_context(type, data)`: Store context data
- `_analyze_context_continuously()`: Background context analysis

### NLPProcessor Class

#### Text Analysis
- `extract_project_elements(text)`: Extract structured elements
- `extract_insights_from_activities(activities)`: Analyze activity patterns
- `generate_suggestions(context)`: Generate AI suggestions

### JiraMCPClient Class

#### Issue Management
- `create_issue(issue)`: Create Jira issue
- `update_issue(key, fields)`: Update existing issue
- `search_issues(jql)`: Search issues with JQL
- `organize_by_mcp(issues)`: Organize issues by MCP methodology

### ChromeRayAutomation Class

#### Browser Control
- `start_chrome()`: Launch Chrome browser
- `execute_action(type, params)`: Execute automation action
- `store_credentials(site, username, password)`: Store login credentials
- `get_automation_history()`: Get execution history

## 🔧 Configuration

### Environment Variables
- `JIRA_BASE_URL`: Your Jira instance URL
- `JIRA_USERNAME`: Jira username/email
- `JIRA_API_TOKEN`: Jira API token
- `JIRA_PROJECT_KEY`: Default project key
- `CHROME_HEADLESS`: Run Chrome in headless mode
- `DEBUG_MODE`: Enable debug logging

### Database Schema
The assistant uses SQLite databases for data persistence:

#### Main Database (`workspace_ai.db`)
- `project_elements`: Stored project elements
- `jira_issues`: Created Jira issues
- `user_context`: User context data
- `quick_actions`: Available quick actions
- `ui_action_log`: Action execution history

#### Credentials Database (`chrome_credentials.db`)
- `credentials`: Stored login credentials
- `automation_history`: Browser automation history

## 📈 Analytics & Reporting

### System Statistics
```python
# Get action statistics
stats = workspace_ai.ui_handler.get_action_stats()
print(f"Total actions: {stats['total_actions']}")
print(f"Success rate: {stats['success_rate']}%")

# Get activity insights
context = workspace_ai._get_current_context()
print(f"Active contexts: {list(context.keys())}")
```

### Performance Metrics
- **Action Success Rate**: Percentage of successful quick actions
- **Processing Time**: Average time for NLP processing
- **Automation Efficiency**: Success rate of Chrome automation
- **Context Relevance**: Accuracy of context-aware suggestions

## 🛡️ Security & Privacy

### Data Protection
- All data stored locally in SQLite databases
- Credentials encrypted at rest (production recommendation)
- No external data transmission without explicit consent
- Automatic cleanup of temporary files

### Privacy Controls
- Opt-in background monitoring
- Selective data collection
- User-controlled data retention
- Secure credential storage

## 🚨 Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
pip install -r requirements.txt
pip install --upgrade selenium ray
```

#### Chrome automation not working
```bash
# Install Chrome WebDriver
# Download from: https://chromedriver.chromium.org/
# Add to PATH or place in project directory
```

#### Jira connection failures
```bash
# Check credentials in .env file
# Verify API token permissions
# Test connection: python -c "from jira_mcp_client import JiraMCPClient; client = JiraMCPClient(); print(client.test_connection())"
```

#### Background monitoring not starting
```bash
# Check permissions for file system access
# Verify database directory exists
# Run with debug: DEBUG_MODE=true python workspace_ai_main.py
```

### Debug Mode
Enable debug logging for troubleshooting:
```bash
DEBUG_MODE=true python workspace_ai_main.py
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd workspace-ai-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings for all functions
- Write unit tests for new features

### Submitting Changes
1. Create feature branch
2. Make changes with tests
3. Update documentation
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for the Cursor AI environment
- Uses Ray for distributed computing
- Selenium for browser automation
- SQLite for data persistence
- NLTK for natural language processing

## 📞 Support

For support, please:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub
4. Contact the development team

---

**Made with ❤️ for the Cursor AI community**