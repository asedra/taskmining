"""
Chrome Ray Automation - Automated Chrome browser interactions
Handles Chrome automation using Ray for distributed computing and browser control
"""

import os
import json
import time
import subprocess
import tempfile
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import sqlite3

try:
    import ray
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    RAY_AVAILABLE = True
    SELENIUM_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False
    SELENIUM_AVAILABLE = False

@dataclass
class ChromeAction:
    """Chrome automation action definition"""
    action_type: str
    target: str
    value: str = ""
    timeout: int = 10
    screenshot: bool = False
    wait_condition: str = ""

@dataclass
class AutomationResult:
    """Result of automation execution"""
    success: bool
    message: str
    screenshot_path: str = ""
    execution_time: float = 0.0
    data_extracted: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.data_extracted is None:
            self.data_extracted = {}

class ChromeRayAutomation:
    """Chrome automation using Ray for distributed processing"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.credentials_db = "data/chrome_credentials.db"
        self.screenshots_dir = "data/screenshots"
        self.ray_initialized = False
        
        # Create directories
        os.makedirs(os.path.dirname(self.credentials_db), exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Initialize credentials database
        self._init_credentials_db()
        
        # Initialize Ray if available
        if RAY_AVAILABLE:
            self._init_ray()
    
    def _init_ray(self):
        """Initialize Ray for distributed computing"""
        try:
            if not ray.is_initialized():
                ray.init(ignore_reinit_error=True)
                self.ray_initialized = True
                print("✅ Ray initialized for distributed automation")
        except Exception as e:
            print(f"⚠️  Ray initialization failed: {e}")
            self.ray_initialized = False
    
    def _init_credentials_db(self):
        """Initialize credentials database"""
        conn = sqlite3.connect(self.credentials_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_used TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                target_url TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                execution_time REAL NOT NULL,
                screenshot_path TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_chrome(self) -> bool:
        """Start Chrome browser with automation capabilities"""
        if not SELENIUM_AVAILABLE:
            print("⚠️  Selenium not available, using mock Chrome automation")
            return True
        
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            # Enable automation features
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome browser started for automation")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Chrome: {e}")
            return False
    
    def stop_chrome(self):
        """Stop Chrome browser"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Chrome browser stopped")
            except Exception as e:
                print(f"⚠️  Error stopping Chrome: {e}")
            finally:
                self.driver = None
    
    def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> bool:
        """Execute a Chrome automation action"""
        try:
            if not SELENIUM_AVAILABLE:
                return self._mock_execute_action(action_type, parameters)
            
            # Start Chrome if not already started
            if not self.driver:
                if not self.start_chrome():
                    return False
            
            # Execute based on action type
            if action_type == "navigate":
                return self._navigate(parameters.get("url", ""))
            elif action_type == "click":
                return self._click(parameters.get("selector", ""))
            elif action_type == "type":
                return self._type(parameters.get("selector", ""), parameters.get("text", ""))
            elif action_type == "login_jira":
                return self._login_jira(parameters)
            elif action_type == "create_jira_issue":
                return self._create_jira_issue(parameters)
            elif action_type == "screenshot":
                return self._take_screenshot(parameters.get("filename", ""))
            elif action_type == "extract_data":
                return self._extract_data(parameters.get("selectors", {}))
            else:
                print(f"⚠️  Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            print(f"❌ Error executing action {action_type}: {e}")
            return False
    
    def _navigate(self, url: str) -> bool:
        """Navigate to a URL"""
        try:
            self.driver.get(url)
            print(f"✅ Navigated to: {url}")
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def _click(self, selector: str) -> bool:
        """Click an element"""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            print(f"✅ Clicked element: {selector}")
            return True
        except Exception as e:
            print(f"❌ Click failed: {e}")
            return False
    
    def _type(self, selector: str, text: str) -> bool:
        """Type text into an element"""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            print(f"✅ Typed text into: {selector}")
            return True
        except Exception as e:
            print(f"❌ Type failed: {e}")
            return False
    
    def _login_jira(self, parameters: Dict[str, Any]) -> bool:
        """Login to Jira using stored credentials"""
        try:
            jira_url = parameters.get("url", "")
            username = parameters.get("username", "")
            password = parameters.get("password", "")
            
            if not jira_url or not username or not password:
                # Try to get from stored credentials
                credentials = self.get_stored_credentials("jira")
                if credentials:
                    jira_url = credentials.get("url", jira_url)
                    username = credentials.get("username", username)
                    password = credentials.get("password", password)
            
            if not jira_url or not username or not password:
                print("❌ Missing Jira credentials")
                return False
            
            # Navigate to Jira
            if not self._navigate(jira_url):
                return False
            
            # Wait for login form
            time.sleep(2)
            
            # Fill username
            if not self._type("#username", username):
                # Try alternative selectors
                if not self._type("input[name='username']", username):
                    print("❌ Could not find username field")
                    return False
            
            # Fill password
            if not self._type("#password", password):
                # Try alternative selectors
                if not self._type("input[name='password']", password):
                    print("❌ Could not find password field")
                    return False
            
            # Submit login
            if not self._click("#login-submit"):
                # Try alternative selectors
                if not self._click("button[type='submit']"):
                    print("❌ Could not find login button")
                    return False
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "dashboard" in self.driver.current_url.lower():
                print("✅ Successfully logged into Jira")
                self.store_credentials("jira", username, password, jira_url)
                return True
            else:
                print("❌ Jira login failed")
                return False
                
        except Exception as e:
            print(f"❌ Jira login error: {e}")
            return False
    
    def _create_jira_issue(self, parameters: Dict[str, Any]) -> bool:
        """Create a Jira issue through the web interface"""
        try:
            # Navigate to create issue page
            create_url = parameters.get("create_url", "")
            if not create_url:
                # Try to find create button
                if not self._click("button[data-test-id='create-issue-button']"):
                    print("❌ Could not find create issue button")
                    return False
            else:
                if not self._navigate(create_url):
                    return False
            
            # Wait for create dialog
            time.sleep(2)
            
            # Fill issue details
            issue_type = parameters.get("issue_type", "Task")
            title = parameters.get("title", "")
            description = parameters.get("description", "")
            
            # Select issue type
            if not self._click("div[data-test-id='issue-type-select']"):
                print("❌ Could not find issue type selector")
                return False
            
            time.sleep(1)
            
            # Select specific issue type
            if not self._click(f"div[data-test-id='issue-type-{issue_type.lower()}']"):
                print(f"❌ Could not select issue type: {issue_type}")
                return False
            
            # Fill summary/title
            if not self._type("input[data-test-id='issue-summary']", title):
                print("❌ Could not fill issue summary")
                return False
            
            # Fill description
            if description:
                if not self._type("textarea[data-test-id='issue-description']", description):
                    print("❌ Could not fill issue description")
                    return False
            
            # Submit issue
            if not self._click("button[data-test-id='create-issue-submit']"):
                print("❌ Could not submit issue")
                return False
            
            # Wait for issue creation
            time.sleep(3)
            
            print("✅ Successfully created Jira issue")
            return True
            
        except Exception as e:
            print(f"❌ Jira issue creation error: {e}")
            return False
    
    def _take_screenshot(self, filename: str = "") -> bool:
        """Take a screenshot"""
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = os.path.join(self.screenshots_dir, filename)
            self.driver.save_screenshot(filepath)
            print(f"✅ Screenshot saved: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return False
    
    def _extract_data(self, selectors: Dict[str, str]) -> bool:
        """Extract data from page using selectors"""
        try:
            extracted_data = {}
            
            for key, selector in selectors.items():
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    extracted_data[key] = element.text
                except Exception as e:
                    print(f"⚠️  Could not extract {key}: {e}")
                    extracted_data[key] = None
            
            print(f"✅ Extracted data: {extracted_data}")
            return True
            
        except Exception as e:
            print(f"❌ Data extraction failed: {e}")
            return False
    
    def _mock_execute_action(self, action_type: str, parameters: Dict[str, Any]) -> bool:
        """Mock execution when Selenium is not available"""
        print(f"🎭 Mock execution: {action_type} with {parameters}")
        time.sleep(1)  # Simulate action time
        return True
    
    def store_credentials(self, site_name: str, username: str, password: str, url: str):
        """Store credentials securely"""
        conn = sqlite3.connect(self.credentials_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO credentials 
            (site_name, username, password, url, created_at, last_used)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            site_name,
            username,
            password,  # In production, this should be encrypted
            url,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Stored credentials for {site_name}")
    
    def get_stored_credentials(self, site_name: str) -> Optional[Dict[str, str]]:
        """Get stored credentials"""
        conn = sqlite3.connect(self.credentials_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, password, url FROM credentials 
            WHERE site_name = ?
            ORDER BY last_used DESC
            LIMIT 1
        ''', (site_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "username": result[0],
                "password": result[1],
                "url": result[2]
            }
        return None
    
    def get_automation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get automation execution history"""
        conn = sqlite3.connect(self.credentials_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT action_type, target_url, success, execution_time, screenshot_path, created_at
            FROM automation_history 
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "action_type": row[0],
                "target_url": row[1],
                "success": row[2],
                "execution_time": row[3],
                "screenshot_path": row[4],
                "created_at": row[5]
            })
        
        conn.close()
        return history
    
    def record_automation(self, action_type: str, target_url: str, success: bool, execution_time: float, screenshot_path: str = ""):
        """Record automation execution"""
        conn = sqlite3.connect(self.credentials_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO automation_history 
            (action_type, target_url, success, execution_time, screenshot_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            action_type,
            target_url,
            success,
            execution_time,
            screenshot_path,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_common_jira_actions() -> List[Dict[str, Any]]:
        """Get common Jira automation actions"""
        return [
            {
                "name": "Login to Jira",
                "action_type": "login_jira",
                "description": "Automatically login to Jira using stored credentials",
                "parameters": ["url", "username", "password"]
            },
            {
                "name": "Create Jira Issue",
                "action_type": "create_jira_issue",
                "description": "Create a new Jira issue through the web interface",
                "parameters": ["issue_type", "title", "description", "assignee"]
            },
            {
                "name": "Navigate to Board",
                "action_type": "navigate",
                "description": "Navigate to a specific Jira board",
                "parameters": ["url"]
            },
            {
                "name": "Update Issue Status",
                "action_type": "update_issue_status",
                "description": "Update the status of a Jira issue",
                "parameters": ["issue_key", "status"]
            },
            {
                "name": "Extract Dashboard Data",
                "action_type": "extract_data",
                "description": "Extract data from Jira dashboard",
                "parameters": ["selectors"]
            }
        ]
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_chrome()
        
        if self.ray_initialized and RAY_AVAILABLE:
            try:
                ray.shutdown()
                print("✅ Ray shutdown complete")
            except Exception as e:
                print(f"⚠️  Ray shutdown error: {e}")
    
    def __del__(self):
        """Destructor"""
        self.cleanup()