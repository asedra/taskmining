# Task Mining Prototype - Project Documentation

## 🎯 Goal

This project aims to prototype a **Task Mining** tool that monitors a user's daily computer activities, including:
- Active window changes
- Keyboard and mouse interactions
- Web browser history
- File downloads and file system changes
- Time spent on running applications

The primary goal is to log these activities and subsequently analyze them to identify manual processes that are candidates for automation.

> ❌ **Note:** This prototype focuses solely on monitoring and analysis. It does *not* provide RPA (Robotic Process Automation) recommendations.

---

## 🗂️ Folder Structure

```yaml
task-mining-prototype/
├── main.py                 # Main control script
├── event_listener.py       # Monitors window changes, keyboard/mouse
├── file_watcher.py         # Monitors file system events (e.g., Downloads)
├── browser_log.py          # Fetches browser history
├── analyzer.py             # Analyzes logged data and generates reports
├── activity_logger.py      # Handles database logging (SQLite)
├── utils/
│   └── time_utils.py       # Utility functions for time/date
├── data/
│   ├── activity.db         # SQLite database for logs
│   └── reports/            # Output directory for analysis reports
└── requirements.txt        # Python dependencies
⚙️ Component Descriptions
1. main.py
The main entry point that initializes and starts all system components.
Monitoring processes run in the background using multiple threads.
2. event_listener.py
Captures active window changes, including the application name and window title.
Logs keyboard and mouse activity events.
Libraries Used: pygetwindow, win32gui, pynput
3. file_watcher.py
Observes all changes (creation, deletion, modification) within a specified directory (e.g., the Downloads folder).
Logs detected file system events to the SQLite database.
Library Used: watchdog
4. browser_log.py
Retrieves the user's Browse history (visited URLs and titles).
Supported Browsers: Chrome, Edge, Firefox.
Automatically updates the history data periodically (e.g., every 5 minutes).
Library Used: browser-history
5. activity_logger.py
Manages the SQLite database (activity.db).
Defines the table structures for storing user activity logs.
Database Schema:

SQL

-- Records application focus, window titles, and input events
CREATE TABLE IF NOT EXISTS user_events (
    timestamp TEXT,     -- ISO 8601 format timestamp
    window_title TEXT,  -- Title of the active window
    application TEXT,   -- Name of the application process
    event_type TEXT,    -- e.g., 'keyboard', 'mouse_click', 'window_change'
    event_details TEXT  -- e.g., key pressed, button clicked, new window title
);

-- Records file system events (creations, deletions, modifications)
CREATE TABLE IF NOT EXISTS file_events (
    timestamp TEXT,     -- ISO 8601 format timestamp
    file_path TEXT,     -- Full path of the affected file
    event_type TEXT     -- e.g., 'created', 'deleted', 'modified', 'moved'
);

-- Records browser history entries
CREATE TABLE IF NOT EXISTS browser_events (
    timestamp TEXT,     -- Visit timestamp (from browser history)
    url TEXT,           -- Visited URL
    title TEXT,         -- Page title
    browser TEXT        -- Browser name (e.g., 'chrome', 'firefox')
);

-- Records time spent in applications
CREATE TABLE IF NOT EXISTS app_usage (
    date TEXT,          -- Date (YYYY-MM-DD)
    application TEXT,   -- Name of the application process
    duration_seconds INTEGER -- Total active duration for that app on that date
);
6. analyzer.py
Processes the data logged in activity.db.
Performs analysis such as:
Calculating time spent in different applications.
Identifying frequently repeated sequences of actions (potential automation candidates).
Summarizing daily Browse patterns.
Generates reports (e.g., in CSV or HTML format) and saves them to the data/reports/ directory.
7. utils/time_utils.py
Contains helper functions for time-related operations, such as:
Getting the current timestamp in a consistent format.
Formatting durations.
🧪 Setup and Execution
Install Dependencies:
Bash

pip install -r requirements.txt
Run the Application:
Bash

python main.py
All logs will be collected in the data/activity.db file.
Analysis reports will be generated in the data/reports/ folder.
✅ Example Use Case Scenario
A user downloads a file from a website using Chrome in the morning.
They open this file in Microsoft Excel and perform some edits.
Finally, they manually copy data from the Excel sheet into an SAP GUI transaction.
Throughout this scenario, the prototype logs:

Web history (download site visit).
File system event (file creation in Downloads).
Application switches (Chrome -> Explorer -> Excel -> SAP GUI).
Keyboard and mouse usage within each application.
The analyzer.py script can then process these logs and potentially highlight this sequence (Download -> Edit in Excel -> Input to SAP) as a time-consuming and repetitive task based on frequency and duration metrics.

📋 Example requirements.txt
pygetwindow
pynput
watchdog
browser-history
psutil
pywin32 # Or pywinauto depending on specific needs
pandas # Likely needed for analyzer.py
📌 Notes
This project is primarily optimized for the Windows operating system due to libraries like pygetwindow and win32gui.
Ethical Considerations: Since this application monitors user behavior, ensure compliance with privacy regulations and obtain necessary consents before deployment. Be transparent about what is being logged.
This structured documentation can be fed into AI code assistants like Cursor AI to facilitate understanding and further development or code generation.