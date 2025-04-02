"""
Kullanıcı aktivitelerini ve olayları kaydetmek için veritabanı işlemleri
"""

import sqlite3
import os
from utils.time_utils import get_current_timestamp, get_current_date

class ActivityLogger:
    def __init__(self, db_path="data/activity.db"):
        """
        Aktivite kayıt sınıfını başlatır
        
        Args:
            db_path: SQLite veritabanı dosya yolu
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
        
    def _connect_db(self):
        """Veritabanına bağlantı oluşturur"""
        conn = sqlite3.connect(self.db_path)
        # Daha hızlı komutlar için WAL modunu etkinleştir
        conn.execute("PRAGMA journal_mode = WAL")
        # Foreign key kısıtlamalarını etkinleştir
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
        
    def _init_db(self):
        """Veritabanı tablolarını oluşturur"""
        conn = self._connect_db()
        cursor = conn.cursor()
        
        # Kullanıcı olayları tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_events (
            timestamp TEXT,     -- ISO 8601 format timestamp
            window_title TEXT,  -- Title of the active window
            application TEXT,   -- Name of the application process
            event_type TEXT,    -- e.g., 'keyboard', 'mouse_click', 'window_change'
            event_details TEXT, -- e.g., key pressed, button clicked, new window title
            screenshot_path TEXT, -- Path to the screenshot image
            screenshot_filename TEXT -- Name of the screenshot file
        )
        """)
        
        # Dosya olayları tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_events (
            timestamp TEXT,     -- ISO 8601 format timestamp
            file_path TEXT,     -- Full path of the affected file
            event_type TEXT     -- e.g., 'created', 'deleted', 'modified', 'moved'
        )
        """)
        
        # Tarayıcı geçmişi tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS browser_events (
            timestamp TEXT,     -- Visit timestamp (from browser history)
            url TEXT,           -- Visited URL
            title TEXT,         -- Page title
            browser TEXT        -- Browser name (e.g., 'chrome', 'firefox')
        )
        """)
        
        # Uygulama kullanım süresi tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_usage (
            date TEXT,          -- Date (YYYY-MM-DD)
            application TEXT,   -- Name of the application process
            duration_seconds INTEGER -- Total active duration for that app on that date
        )
        """)
        
        conn.commit()
        conn.close()
        
    def log_user_event(self, window_title, application, event_type, event_details="", screenshot_path=None, screenshot_filename=None):
        """
        Kullanıcı aktivitesini kaydeder
        
        Args:
            window_title: Aktif pencere başlığı
            application: Uygulama adı
            event_type: Olay türü (keyboard, mouse_click, window_change, vb.)
            event_details: Olay detayları
            screenshot_path: Ekran görüntüsü dosya yolu
            screenshot_filename: Ekran görüntüsü dosya adı
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        timestamp = get_current_timestamp()
        
        cursor.execute(
            "INSERT INTO user_events VALUES (?, ?, ?, ?, ?, ?, ?)",
            (timestamp, window_title, application, event_type, event_details, screenshot_path, screenshot_filename)
        )
        
        conn.commit()
        conn.close()
        
    def log_file_event(self, file_path, event_type):
        """
        Dosya olayını kaydeder
        
        Args:
            file_path: Dosya yolu
            event_type: Olay türü (created, deleted, modified, moved)
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        timestamp = get_current_timestamp()
        
        cursor.execute(
            "INSERT INTO file_events VALUES (?, ?, ?)",
            (timestamp, file_path, event_type)
        )
        
        conn.commit()
        conn.close()
        
    def log_browser_event(self, url, title, browser, timestamp=None):
        """
        Tarayıcı aktivitesini kaydeder
        
        Args:
            url: Ziyaret edilen URL
            title: Sayfa başlığı
            browser: Tarayıcı adı
            timestamp: Ziyaret zamanı (None ise şu anki zaman)
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        if timestamp is None:
            timestamp = get_current_timestamp()
        
        # Varolan bir kaydı kontrol et (aynı URL ve timestamp için)
        cursor.execute(
            "SELECT COUNT(*) FROM browser_events WHERE url = ? AND timestamp = ?",
            (url, timestamp)
        )
        
        if cursor.fetchone()[0] == 0:  # Eğer kayıt yoksa ekle
            cursor.execute(
                "INSERT INTO browser_events VALUES (?, ?, ?, ?)",
                (timestamp, url, title, browser)
            )
        
        conn.commit()
        conn.close()
        
    def update_app_usage(self, application, duration_seconds, date=None):
        """
        Uygulama kullanım süresini günceller
        
        Args:
            application: Uygulama adı
            duration_seconds: Saniye cinsinden süre
            date: Tarih (None ise bugün)
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        if date is None:
            date = get_current_date()
        
        # Önce mevcut kaydı kontrol et
        cursor.execute(
            "SELECT duration_seconds FROM app_usage WHERE date = ? AND application = ?",
            (date, application)
        )
        
        result = cursor.fetchone()
        
        if result:
            # Kayıt varsa güncelle
            current_duration = result[0]
            cursor.execute(
                "UPDATE app_usage SET duration_seconds = ? WHERE date = ? AND application = ?",
                (current_duration + duration_seconds, date, application)
            )
        else:
            # Kayıt yoksa yeni ekle
            cursor.execute(
                "INSERT INTO app_usage VALUES (?, ?, ?)",
                (date, application, duration_seconds)
            )
        
        conn.commit()
        conn.close()
        
    def get_app_usage(self, date=None, days=1):
        """
        Belirli bir gün veya dönem için uygulama kullanımını alır
        
        Args:
            date: Başlangıç tarihi (None ise bugün)
            days: Kaç gün geriye gidileceği
            
        Returns:
            list: Uygulama kullanım kayıtları listesi
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        if date is None:
            date = get_current_date()
            
        if days > 1:
            # Tarih aralığı için sorgu
            cursor.execute(
                """
                SELECT date, application, duration_seconds 
                FROM app_usage 
                WHERE date <= ? 
                ORDER BY date DESC
                LIMIT ?
                """,
                (date, days)
            )
        else:
            # Tek gün için sorgu
            cursor.execute(
                "SELECT date, application, duration_seconds FROM app_usage WHERE date = ?",
                (date,)
            )
            
        result = cursor.fetchall()
        conn.close()
        
        return result
    
    def get_user_events(self, event_type=None, start_time=None, end_time=None, limit=100):
        """
        Kullanıcı olaylarını sorgular
        
        Args:
            event_type: Olay türü filtresi (None ise tümü)
            start_time: Başlangıç zamanı
            end_time: Bitiş zamanı
            limit: Maksimum kayıt sayısı
            
        Returns:
            list: Kullanıcı olayları listesi
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        query = "SELECT * FROM user_events"
        params = []
        where_clauses = []
        
        if event_type:
            where_clauses.append("event_type = ?")
            params.append(event_type)
            
        if start_time:
            where_clauses.append("timestamp >= ?")
            params.append(start_time)
            
        if end_time:
            where_clauses.append("timestamp <= ?")
            params.append(end_time)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.close()
        
        return result
    
    def get_file_events(self, event_type=None, start_time=None, end_time=None, limit=100):
        """
        Dosya olaylarını sorgular
        
        Args:
            event_type: Olay türü filtresi (None ise tümü)
            start_time: Başlangıç zamanı
            end_time: Bitiş zamanı
            limit: Maksimum kayıt sayısı
            
        Returns:
            list: Dosya olayları listesi
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        query = "SELECT * FROM file_events"
        params = []
        where_clauses = []
        
        if event_type:
            where_clauses.append("event_type = ?")
            params.append(event_type)
            
        if start_time:
            where_clauses.append("timestamp >= ?")
            params.append(start_time)
            
        if end_time:
            where_clauses.append("timestamp <= ?")
            params.append(end_time)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.close()
        
        return result
    
    def get_browser_events(self, browser=None, start_time=None, end_time=None, limit=100):
        """
        Tarayıcı olaylarını sorgular
        
        Args:
            browser: Tarayıcı filtresi (None ise tümü)
            start_time: Başlangıç zamanı
            end_time: Bitiş zamanı
            limit: Maksimum kayıt sayısı
            
        Returns:
            list: Tarayıcı olayları listesi
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        query = "SELECT * FROM browser_events"
        params = []
        where_clauses = []
        
        if browser:
            where_clauses.append("browser = ?")
            params.append(browser)
            
        if start_time:
            where_clauses.append("timestamp >= ?")
            params.append(start_time)
            
        if end_time:
            where_clauses.append("timestamp <= ?")
            params.append(end_time)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.close()
        
        return result

    def get_events_with_screenshots(self, limit=10):
        """
        Ekran görüntüsü olan olayları ve detaylarını getirir
        
        Args:
            limit: Maksimum kayıt sayısı
            
        Returns:
            list: Olay ve ekran görüntüsü detayları
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            timestamp,
            window_title,
            application,
            event_type,
            event_details,
            screenshot_path
        FROM user_events
        WHERE screenshot_path IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        result = cursor.fetchall()
        conn.close()
        
        return result

    def get_event_screenshot_pairs(self, event_type=None, start_time=None, end_time=None, limit=10):
        """
        Belirli bir olay türü için ekran görüntüsü ve olay eşleşmelerini getirir
        
        Args:
            event_type: Olay türü (keyboard, mouse_click)
            start_time: Başlangıç zamanı
            end_time: Bitiş zamanı
            limit: Maksimum kayıt sayısı
            
        Returns:
            list: Olay ve ekran görüntüsü eşleşmeleri
        """
        conn = self._connect_db()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            timestamp,
            window_title,
            application,
            event_type,
            event_details,
            screenshot_path
        FROM user_events
        WHERE screenshot_path IS NOT NULL
        """
        
        params = []
        where_clauses = []
        
        if event_type:
            where_clauses.append("event_type = ?")
            params.append(event_type)
            
        if start_time:
            where_clauses.append("timestamp >= ?")
            params.append(start_time)
            
        if end_time:
            where_clauses.append("timestamp <= ?")
            params.append(end_time)
            
        if where_clauses:
            query += " AND " + " AND ".join(where_clauses)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.close()
        
        return result 