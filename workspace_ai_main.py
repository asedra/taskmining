#!/usr/bin/env python3
"""
Workspace AI Assistant - Main Startup Script
Integrates task mining with AI-powered project management and automation
"""

import sys
import os
import time
import signal
import threading
from datetime import datetime
from workspace_ai_assistant import WorkspaceAIAssistant, workspace_ai

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    if workspace_ai.is_monitoring:
        workspace_ai.stop_background_monitoring()
    sys.exit(0)

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def print_banner():
    """Print the startup banner"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                       🚀 WORKSPACE AI ASSISTANT 🚀                          ║
║                                                                               ║
║  Advanced AI automation for Cursor environment                               ║
║  • Background monitoring and analysis                                        ║
║  • Natural language processing for projects                                  ║
║  • Jira integration with MCP methodology                                     ║
║  • Chrome automation with Ray                                                ║
║  • Quick action buttons for rapid task execution                             ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

def test_components():
    """Test all AI assistant components"""
    print("\n🔍 Testing AI Assistant Components...")
    
    # Test NLP Processor
    print("  📝 Testing NLP Processor...")
    test_text = "I want to create a new project management system with automated workflows and risk analysis."
    element = workspace_ai.process_natural_language_input(test_text)
    if element.vision:
        print(f"    ✅ NLP: Extracted vision: {element.vision[:50]}...")
    else:
        print("    ⚠️  NLP: No vision extracted")
    
    # Test Jira MCP Client
    print("  🎯 Testing Jira MCP Client...")
    jira_status = workspace_ai.jira_client.test_connection()
    if jira_status:
        print("    ✅ Jira: Connection successful")
    else:
        print("    ⚠️  Jira: Using mock mode (no credentials)")
    
    # Test Chrome Automation
    print("  🌐 Testing Chrome Automation...")
    chrome_result = workspace_ai.chrome_automation.execute_action("test", {"mock": True})
    if chrome_result:
        print("    ✅ Chrome: Automation ready")
    else:
        print("    ⚠️  Chrome: Automation not available")
    
    # Test Quick Actions
    print("  ⚡ Testing Quick Actions...")
    actions = workspace_ai.get_quick_actions()
    if actions:
        print(f"    ✅ Quick Actions: {len(actions)} actions available")
    else:
        print("    ⚠️  Quick Actions: No actions available")
    
    print("  🔧 Component testing complete\n")

def demonstrate_features():
    """Demonstrate key features of the AI Assistant"""
    print("🎯 AI Assistant Feature Demonstration:\n")
    
    # 1. Natural Language Processing
    print("1. 📝 Natural Language Processing:")
    sample_input = """
    Vision: Build an AI-powered task management system
    Scope: User interface, backend API, AI recommendations
    Risks: Data privacy, performance issues, user adoption
    Milestones: MVP completion, Beta testing, Production launch
    Deliverables: Web app, Mobile app, API documentation
    Dependencies: AI models, Cloud infrastructure, Security audit
    Priority: High
    """
    
    element = workspace_ai.process_natural_language_input(sample_input)
    print(f"   Vision: {element.vision}")
    print(f"   Scope: {', '.join(element.scope[:3])}")
    print(f"   Risks: {', '.join(element.risks[:2])}")
    print(f"   Priority: {element.priority}")
    print()
    
    # 2. Jira Issue Creation
    print("2. 🎯 Jira Issue Creation (MCP Methodology):")
    jira_issues = workspace_ai.create_jira_issues(element)
    for issue in jira_issues:
        print(f"   {issue.issue_type}: {issue.title}")
    print()
    
    # 3. Quick Actions
    print("3. ⚡ Quick Actions Available:")
    actions = workspace_ai.get_quick_actions()
    for action in actions[:4]:  # Show first 4
        print(f"   • {action['title']}: {action['description']}")
    print()
    
    # 4. Chrome Automation
    print("4. 🌐 Chrome Automation Capabilities:")
    chrome_actions = workspace_ai.chrome_automation.get_common_jira_actions()
    for action in chrome_actions[:3]:  # Show first 3
        print(f"   • {action['name']}: {action['description']}")
    print()

def interactive_mode():
    """Run interactive mode for testing commands"""
    print("🎮 Interactive Mode - Type commands to test the AI Assistant")
    print("Commands:")
    print("  'process <text>' - Process natural language input")
    print("  'actions' - Show available quick actions")
    print("  'stats' - Show system statistics")
    print("  'help' - Show this help")
    print("  'quit' - Exit interactive mode")
    print()
    
    while True:
        try:
            command = input("AI Assistant > ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
            elif command.lower() == 'help':
                print("Available commands: process, actions, stats, help, quit")
            elif command.lower() == 'actions':
                actions = workspace_ai.get_quick_actions()
                print(f"Available actions ({len(actions)}):")
                for i, action in enumerate(actions[:5], 1):
                    print(f"  {i}. {action['title']}")
            elif command.lower() == 'stats':
                stats = workspace_ai.ui_handler.get_action_stats()
                print(f"System Statistics:")
                print(f"  Total Actions: {stats['total_actions']}")
                print(f"  Success Rate: {stats['success_rate']}%")
                print(f"  Common Actions: {len(stats['common_actions'])}")
            elif command.lower().startswith('process '):
                text = command[8:]  # Remove 'process ' prefix
                if text:
                    element = workspace_ai.process_natural_language_input(text)
                    print(f"Processed: {element.vision}")
                    print(f"Category: {element.category}")
                    print(f"Priority: {element.priority}")
                else:
                    print("Please provide text to process")
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n👋 Exiting interactive mode")

def main():
    """Main function"""
    print_banner()
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Test components
    test_components()
    
    # Demonstrate features
    demonstrate_features()
    
    # Start background monitoring
    print("🚀 Starting Background Monitoring...")
    workspace_ai.start_background_monitoring()
    
    # Show menu
    while True:
        print("\n" + "="*60)
        print("🎛️  WORKSPACE AI ASSISTANT CONTROL PANEL")
        print("="*60)
        print("1. 🎮 Interactive Mode")
        print("2. 📊 View System Statistics")
        print("3. 🎯 Create Sample Jira Issues")
        print("4. 🌐 Test Chrome Automation")
        print("5. ⚡ Test Quick Actions")
        print("6. 🔍 View Activity Analysis")
        print("7. ⏹️  Stop Background Monitoring")
        print("8. 🚪 Exit")
        print("="*60)
        
        try:
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == '1':
                interactive_mode()
            elif choice == '2':
                stats = workspace_ai.ui_handler.get_action_stats()
                print(f"\n📊 System Statistics:")
                print(f"  Total Actions Executed: {stats['total_actions']}")
                print(f"  Success Rate: {stats['success_rate']}%")
                print(f"  Monitoring Status: {'Active' if workspace_ai.is_monitoring else 'Inactive'}")
                input("\nPress Enter to continue...")
            elif choice == '3':
                print("\n🎯 Creating Sample Jira Issues...")
                sample_text = "Create a user dashboard with analytics and reporting features"
                element = workspace_ai.process_natural_language_input(sample_text)
                issues = workspace_ai.create_jira_issues(element)
                print(f"Created {len(issues)} Jira issues")
                input("\nPress Enter to continue...")
            elif choice == '4':
                print("\n🌐 Testing Chrome Automation...")
                result = workspace_ai.chrome_automation.execute_action("test", {"url": "https://example.com"})
                print(f"Chrome automation result: {result}")
                input("\nPress Enter to continue...")
            elif choice == '5':
                print("\n⚡ Testing Quick Actions...")
                test_action = workspace_ai.execute_quick_action("summarize_content", {
                    "selected_text": "This is a test text for summarization",
                    "action_type": "summarize"
                })
                print(f"Quick action result: {test_action.get('message', 'No message')}")
                input("\nPress Enter to continue...")
            elif choice == '6':
                print("\n🔍 Activity Analysis:")
                context = workspace_ai._get_current_context()
                print(f"Context categories: {list(context.keys())}")
                print(f"Total context items: {sum(len(v) for v in context.values())}")
                input("\nPress Enter to continue...")
            elif choice == '7':
                if workspace_ai.is_monitoring:
                    workspace_ai.stop_background_monitoring()
                    print("⏹️  Background monitoring stopped")
                else:
                    print("⚠️  Background monitoring is not active")
                input("\nPress Enter to continue...")
            elif choice == '8':
                print("\n👋 Goodbye! Shutting down Workspace AI Assistant...")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown requested by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    # Cleanup
    if workspace_ai.is_monitoring:
        workspace_ai.stop_background_monitoring()
    
    print("\n✅ Workspace AI Assistant shutdown complete")

if __name__ == "__main__":
    main()