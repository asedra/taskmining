# PM Assistant Setup Guide

This guide will help you set up and configure the PM Assistant for integration with your Task Mining project and Jira.

## Prerequisites

- Python 3.7+ with existing Task Mining project
- Node.js 16+ (for MCP servers)
- Jira instance with API access
- Cursor AI with MCP support

## Step 1: Install Dependencies

### Python Dependencies

```bash
# Install additional PM Assistant dependencies
pip install -r requirements.txt
```

### Node.js Dependencies (for MCP servers)

```bash
# Initialize npm project for MCP servers
npm init -y

# Install required packages
npm install https request
```

## Step 2: Configure Jira Integration

### Create Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "PM Assistant")
4. Copy the generated token

### Set Environment Variables

Create a `.env` file in your project root:

```bash
# Jira Configuration
JIRA_BASE_URL=your-instance.atlassian.net
JIRA_API_TOKEN=your-api-token-here
JIRA_USERNAME=your-email@domain.com

# Optional: Project Configuration
DEFAULT_PROJECT_KEY=PROJ
DEFAULT_PROJECT_NAME=Arketic
```

Load environment variables:

```bash
# Linux/Mac
source .env

# Windows
set JIRA_BASE_URL=your-instance.atlassian.net
set JIRA_API_TOKEN=your-api-token-here
set JIRA_USERNAME=your-email@domain.com
```

## Step 3: Verify MCP Configuration

The `.cursor/mcp.json` file should already be configured. Verify it exists and contains:

```json
{
  "servers": [
    {
      "name": "jira",
      "command": "node",
      "args": ["./pm_assistant/mcp_servers/jira_server.js"],
      "env": {
        "JIRA_BASE_URL": "your-jira-instance.atlassian.net",
        "JIRA_API_TOKEN": "your-api-token",
        "JIRA_USERNAME": "your-email@domain.com"
      }
    }
  ],
  "client": {
    "name": "pm-assistant",
    "version": "1.0.0"
  }
}
```

## Step 4: Test Installation

### Basic Functionality Test

```bash
# Run the PM Assistant integration test
python main_pm_assistant.py
```

Expected output:
```
PM Assistant Integration - Test Mode
==================================================
PM Assistant Integration initialized for project: Arketic
Analyzing test input...
Generated 4 project ideas
Testing Jira synchronization...
Sync result: {'epics_created': [...], 'stories_created': [...]}
Generating project report...
Report generated: data/reports/Arketic_comprehensive_report_20250704_123456.md
Testing project knowledge search...
Search returned 4 results
PM Assistant Integration test completed!
```

### Test Individual Components

```python
# Test PM Assistant core
from pm_assistant import PMAssistant

pm = PMAssistant("TestProject")
result = pm.analyze_input("We need to create a test API for user management")
print(f"Analysis result: {result}")
```

```python
# Test Jira integration
from pm_assistant.integrations.jira_integration import JiraIntegration

jira = JiraIntegration()
epic_result = jira.create_epic({
    "summary": "Test Epic",
    "description": "This is a test epic",
    "labels": ["test"]
})
print(f"Epic creation result: {epic_result}")
```

```python
# Test memory manager
from pm_assistant.core.memory_manager import MemoryManager

mm = MemoryManager()
ideas = mm.get_all_ideas()
print(f"Found {len(ideas)} existing ideas")
```

## Step 5: Integration with Existing Task Mining

### Update Main Script

Modify your existing `main.py` to include PM Assistant:

```python
# Add to existing main.py
from main_pm_assistant import PMAssistantIntegration

# Initialize PM Assistant alongside existing components
pm_assistant = PMAssistantIntegration("YourProjectName")

# Add PM analysis to your existing workflow
def analyze_project_context(user_input):
    """Add this function to analyze project management context"""
    return pm_assistant.analyze_user_input(user_input)
```

### Enhance Existing Reports

Update your `analyzer.py` to include PM insights:

```python
# Add to analyzer.py
from main_pm_assistant import PMAssistantIntegration

class EnhancedAnalyzer:
    def __init__(self):
        self.pm_assistant = PMAssistantIntegration()
    
    def generate_comprehensive_report(self):
        """Enhanced report with PM data"""
        # Your existing analysis code
        existing_report = self.generate_daily_report()
        
        # Add PM insights
        pm_report = self.pm_assistant.generate_project_report()
        
        return f"{existing_report}\n\n{pm_report}"
```

## Step 6: Directory Structure Verification

Ensure your project structure looks like this:

```
your-project/
├── .cursor/
│   └── mcp.json
├── pm_assistant/
│   ├── __init__.py
│   ├── core/
│   │   ├── pm_assistant.py
│   │   ├── memory_manager.py
│   │   └── project_manager.py
│   ├── integrations/
│   │   └── jira_integration.py
│   ├── utils/
│   │   └── pmi_utils.py
│   └── mcp_servers/
│       ├── jira_server.js
│       └── package.json
├── data/
│   ├── pm_assistant.db (created automatically)
│   └── reports/
├── main_pm_assistant.py
├── requirements.txt
└── .env
```

## Step 7: Test Jira Connectivity

### Manual Jira Test

```bash
# Test Jira API connectivity manually
curl -X GET \
  -H "Authorization: Basic $(echo -n 'your-email:your-api-token' | base64)" \
  -H "Accept: application/json" \
  "https://your-instance.atlassian.net/rest/api/2/myself"
```

### MCP Server Test

```bash
# Test MCP server manually
cd pm_assistant/mcp_servers
node jira_server.js

# In another terminal, send test request
echo '{"jsonrpc":"2.0","id":1,"method":"create_epic","params":{"summary":"Test Epic","description":"Test"}}' | node jira_server.js
```

## Step 8: Configure Cursor AI

### Enable MCP in Cursor

1. Open Cursor AI
2. Go to Settings → Features
3. Enable "Model Context Protocol (MCP)"
4. Restart Cursor

### Verify MCP Integration

In Cursor, the PM Assistant should now have access to:

- Jira issue creation and management
- Project context and memory
- Activity data from Task Mining
- Automated documentation generation

## Troubleshooting

### Common Setup Issues

1. **Environment Variables Not Loading**
   ```bash
   # Verify variables are set
   echo $JIRA_BASE_URL
   echo $JIRA_API_TOKEN
   
   # If empty, source .env file again
   source .env
   ```

2. **Module Import Errors**
   ```bash
   # Add project root to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   
   # Or run with module flag
   python -m main_pm_assistant
   ```

3. **Database Creation Errors**
   ```bash
   # Ensure data directory exists and is writable
   mkdir -p data/reports
   chmod 755 data
   ```

4. **Node.js MCP Server Errors**
   ```bash
   # Verify Node.js version
   node --version  # Should be 16+
   
   # Install missing dependencies
   cd pm_assistant/mcp_servers
   npm install
   ```

5. **Jira Authentication Errors**
   ```bash
   # Test Jira credentials manually
   curl -X GET \
     -H "Authorization: Basic $(echo -n 'email:token' | base64)" \
     "https://your-instance.atlassian.net/rest/api/2/myself"
   ```

### Performance Optimization

1. **Database Optimization**
   ```python
   # Clean up old data periodically
   from pm_assistant.core.memory_manager import MemoryManager
   mm = MemoryManager()
   mm.cleanup_old_data(30)  # Keep last 30 days
   ```

2. **Memory Usage**
   ```python
   # Monitor memory usage
   import psutil
   process = psutil.Process()
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
   ```

## Next Steps

After successful setup:

1. **Explore the API**: Try different input analysis scenarios
2. **Customize Categories**: Modify PMI categories for your specific needs
3. **Enhance Integration**: Add custom activity correlations
4. **Configure Dashboards**: Set up regular reporting schedules
5. **Train Team**: Share documentation with team members

## Support

If you encounter issues during setup:

1. Check the logs in `data/pm_assistant.log`
2. Verify all environment variables are correctly set
3. Test individual components in isolation
4. Review the troubleshooting section above
5. Check Jira instance permissions and API access

For additional help, refer to the main PM Assistant documentation in `PM_ASSISTANT_DOCUMENTATION.md`.