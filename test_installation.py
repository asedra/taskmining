#!/usr/bin/env python3
"""
Test Installation Script for Workspace AI Assistant
Verifies that all components are installed and working correctly
"""

import sys
import os
import traceback
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        "sqlite3",
        "json",
        "datetime",
        "threading",
        "typing"
    ]
    
    optional_modules = [
        ("selenium", "Chrome automation will not be available"),
        ("ray", "Distributed computing will not be available"),
        ("nltk", "Advanced NLP features will be limited"),
        ("requests", "HTTP requests will not work"),
        ("pandas", "Data analysis features will be limited"),
        ("matplotlib", "Visualization features will not work")
    ]
    
    # Test required modules
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - REQUIRED")
            return False
    
    # Test optional modules
    for module, warning in optional_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ⚠️  {module} - {warning}")
    
    return True

def test_workspace_ai_imports():
    """Test Workspace AI specific imports"""
    print("\n🧠 Testing Workspace AI components...")
    
    components = [
        "workspace_ai_assistant",
        "nlp_processor", 
        "jira_mcp_client",
        "chrome_ray_automation",
        "ui_action_handler"
    ]
    
    success = True
    for component in components:
        try:
            __import__(component)
            print(f"  ✅ {component}")
        except ImportError as e:
            print(f"  ❌ {component} - {str(e)}")
            success = False
        except Exception as e:
            print(f"  ⚠️  {component} - {str(e)}")
    
    return success

def test_database_creation():
    """Test database creation and initialization"""
    print("\n💾 Testing database operations...")
    
    try:
        from workspace_ai_assistant import WorkspaceAIAssistant
        
        # Create test instance
        test_db_path = "data/test_workspace_ai.db"
        assistant = WorkspaceAIAssistant(test_db_path)
        
        print("  ✅ Database creation successful")
        
        # Test basic operations
        assistant._store_user_context("test", {"test_data": "test_value"})
        context = assistant._get_current_context()
        
        print("  ✅ Database operations successful")
        
        # Cleanup
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            print("  ✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {str(e)}")
        return False

def test_nlp_processing():
    """Test NLP processing functionality"""
    print("\n📝 Testing NLP processing...")
    
    try:
        from nlp_processor import NLPProcessor
        
        processor = NLPProcessor()
        test_text = "Vision: Create a test project with automated workflows"
        
        element = processor.extract_project_elements(test_text)
        
        if element.vision:
            print(f"  ✅ NLP extraction successful: {element.vision[:30]}...")
        else:
            print("  ⚠️  NLP extraction returned empty vision")
        
        return True
        
    except Exception as e:
        print(f"  ❌ NLP test failed: {str(e)}")
        return False

def test_jira_client():
    """Test Jira client (mock mode)"""
    print("\n🎯 Testing Jira client...")
    
    try:
        from jira_mcp_client import JiraMCPClient, JiraIssue
        
        client = JiraMCPClient()
        
        # Test connection (should fail gracefully without credentials)
        connection_status = client.test_connection()
        if connection_status:
            print("  ✅ Jira connection successful")
        else:
            print("  ⚠️  Jira connection failed (expected without credentials)")
        
        # Test mock issue creation
        test_issue = JiraIssue(
            issue_type="Task",
            title="Test Issue",
            description="Test Description"
        )
        
        created_issue = client.create_issue(test_issue)
        if created_issue and created_issue.jira_key:
            print(f"  ✅ Issue creation successful: {created_issue.jira_key}")
        else:
            print("  ❌ Issue creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Jira client test failed: {str(e)}")
        return False

def test_chrome_automation():
    """Test Chrome automation (mock mode)"""
    print("\n🌐 Testing Chrome automation...")
    
    try:
        from chrome_ray_automation import ChromeRayAutomation
        
        automation = ChromeRayAutomation()
        
        # Test mock execution
        result = automation.execute_action("test", {"mock": True})
        
        if result:
            print("  ✅ Chrome automation test successful")
        else:
            print("  ❌ Chrome automation test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Chrome automation test failed: {str(e)}")
        return False

def test_ui_actions():
    """Test UI action handler"""
    print("\n⚡ Testing UI action handler...")
    
    try:
        from ui_action_handler import UIActionHandler
        
        handler = UIActionHandler("data/test_ui_actions.db")
        
        # Test action execution
        result = handler.execute_action("summarize_content", {
            "selected_text": "This is a test text for summarization",
            "action_type": "summarize"
        })
        
        if result.get("success"):
            print("  ✅ UI action execution successful")
        else:
            print(f"  ❌ UI action execution failed: {result.get('error')}")
            return False
        
        # Cleanup
        test_db = "data/test_ui_actions.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        return True
        
    except Exception as e:
        print(f"  ❌ UI action test failed: {str(e)}")
        return False

def test_full_integration():
    """Test full system integration"""
    print("\n🔧 Testing full system integration...")
    
    try:
        from workspace_ai_assistant import workspace_ai
        
        # Test natural language processing
        test_input = "Vision: Test integration with basic project setup"
        element = workspace_ai.process_natural_language_input(test_input)
        
        if not element.vision:
            print("  ❌ Integration test failed: No vision extracted")
            return False
        
        print(f"  ✅ Vision extracted: {element.vision[:30]}...")
        
        # Test quick actions
        actions = workspace_ai.get_quick_actions()
        if not actions:
            print("  ❌ Integration test failed: No quick actions available")
            return False
        
        print(f"  ✅ Quick actions available: {len(actions)}")
        
        # Test action execution
        result = workspace_ai.execute_quick_action("summarize_content", {
            "selected_text": "Test text for integration",
            "action_type": "summarize"
        })
        
        if not result.get("success"):
            print(f"  ❌ Integration test failed: {result.get('error')}")
            return False
        
        print("  ✅ Full integration test successful")
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {str(e)}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 Starting Workspace AI Assistant Installation Test")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_imports),
        ("Workspace AI Imports", test_workspace_ai_imports),
        ("Database Operations", test_database_creation),
        ("NLP Processing", test_nlp_processing),
        ("Jira Client", test_jira_client),
        ("Chrome Automation", test_chrome_automation),
        ("UI Actions", test_ui_actions),
        ("Full Integration", test_full_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  💥 {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
        if success:
            passed += 1
    
    print("-" * 60)
    print(f"  📈 Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Workspace AI Assistant is ready to use.")
        print("   Run 'python workspace_ai_main.py' to start the assistant.")
    elif passed >= total * 0.7:
        print("\n⚠️  Most tests passed. Some optional features may not work correctly.")
        print("   Check the failed tests above and install missing dependencies.")
    else:
        print("\n❌ Multiple tests failed. Please check your installation.")
        print("   Install missing dependencies: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)