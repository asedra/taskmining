"""
Tarayıcı geçmişini izler ve kaydeder (Sadece Chrome desteklenir)
"""

import time
import threading
import os
import sqlite3
import shutil
import platform
from datetime import datetime, timedelta
import subprocess

class BrowserLogger:
    def __init__(self, activity_logger, interval=10, callback=None):
        """
        Tarayıcı geçmişi kaydediciyi başlatır
        
        Args:
            activity_logger: Aktivite kaydedici
            interval: Güncellemeler arasındaki saniye cinsinden süre (varsayılan: 10 saniye)
            callback: Yeni kayıtlar bulunduğunda çağrılacak fonksiyon (parametre: bulunan kayıt sayısı)
        """
        self.logger = activity_logger
        self.interval = interval
        self.running = False
        self.last_fetch_time = None
        self.callback = callback
        
        # Chrome profil yolunu belirle
        self.user_data_path = self._determine_chrome_path()
        self.history_path = os.path.join(self.user_data_path, "History") if self.user_data_path else None
        
        # Sqlite dosyasının kopyasının saklanacağı geçici dizin
        self.temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def _determine_chrome_path(self):
        """Chrome tarayıcısının profil dizinini belirler"""
        system = platform.system()
        try:
            if system == "Windows":
                return os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Default"
            elif system == "Darwin":  # MacOS
                return os.path.expanduser('~') + "/Library/Application Support/Google/Chrome/Default"
            elif system == "Linux":
                return os.path.expanduser('~') + "/.config/google-chrome/Default"
        except Exception as e:
            print(f"Chrome profil dizini belirlenirken hata: {e}")
            return None
            
    def _ensure_chrome_is_active(self):
        """Chrome'un aktif durumda olup olmadığını kontrol eder ve gerekirse başlatır"""
        try:
            # Chrome'un çalışıp çalışmadığını kontrol et
            is_running = False
            if platform.system() == "Windows":
                # Windows'ta process durumunu kontrol et
                output = subprocess.check_output("tasklist", shell=True).decode()
                is_running = "chrome.exe" in output
                
                if not is_running:
                    # Chrome'u arkaplanda başlat
                    print("Chrome aktif değil. Otomatik olarak başlatılıyor...")
                    subprocess.Popen(
                        r'start chrome "about:blank"',
                        shell=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE
                    )
                    # Chrome'un başlaması için biraz bekle
                    time.sleep(3)
                    return True
            
            return is_running
        except Exception as e:
            print(f"Chrome durumu kontrol edilirken hata: {e}")
            return False
    
    def _fetch_chrome_history(self):
        """
        Chrome tarayıcısının son tarama geçmişini getirir
        
        Returns:
            list: Ziyaret edilen sayfaların listesi
        """
        try:
            # Chrome tarayıcısının aktif olup olmadığını kontrol et
            self._ensure_chrome_is_active()
            
            if not self.history_path or not os.path.exists(self.history_path):
                print("Chrome tarayıcısı kurulu değil veya geçmiş dosyası bulunamadı.")
                return []
                
            # Chrome geçmiş dosyası kullanım sırasında kilitli olabilir, bu nedenle kopyasını alıp kullanacağız
            timestamp = int(time.time())
            temp_history = os.path.join(self.temp_dir, f"History_temp_{timestamp}")
            
            # Dosyayı kopyala
            try:
                shutil.copy2(self.history_path, temp_history)
            except Exception as e:
                print(f"Geçmiş dosyası kopyalanamadı: {e}")
                return []
                
            try:
                # SQLite veritabanını aç
                conn = sqlite3.connect(temp_history)
                cursor = conn.cursor()
                
                # Son kontrol zamanından sonraki girişleri al
                if self.last_fetch_time:
                    # timestamp_microseconds'i UNIX epoch time'dan Chrome'un zaman formatına dönüştür
                    # Chrome epoch zamanı: 1601-01-01T00:00:00Z'dan itibaren mikrosaniye
                    # Unix epoch zamanı: 1970-01-01T00:00:00Z'dan itibaren saniye
                    # Dönüşüm faktörü: (369 yıl + 89 gün) * 86400 * 1000000 mikrosaniye
                    chrome_epoch_start = 11644473600000000  # Chrome epoch başlangıcı (UNIX epoch ile fark, mikrosaniye)
                    
                    # Son ziyaret edilen sayfaları bul
                    # last_visit_time Chrome'un mikrosaniye formatında
                    last_fetch_unix = int(self.last_fetch_time.timestamp() * 1000000)  # mikrosaniyeye çevir
                    chrome_time = last_fetch_unix + chrome_epoch_start
                    
                    cursor.execute("""
                        SELECT datetime(last_visit_time/1000000-11644473600, 'unixepoch', 'localtime'), 
                               url, title
                        FROM urls
                        WHERE last_visit_time > ?
                        ORDER BY last_visit_time DESC
                    """, (chrome_time,))
                else:
                    # İlk çalıştırmada son 5 dakikadaki girişleri al
                    five_min_ago = int((datetime.now() - timedelta(minutes=5)).timestamp() * 1000000) + 11644473600000000
                    
                    cursor.execute("""
                        SELECT datetime(last_visit_time/1000000-11644473600, 'unixepoch', 'localtime'), 
                               url, title
                        FROM urls
                        WHERE last_visit_time > ?
                        ORDER BY last_visit_time DESC
                    """, (five_min_ago,))
                
                # Sonuçları al
                results = cursor.fetchall()
                conn.close()
                
                # Geçici dosyayı sil
                try:
                    os.remove(temp_history)
                except:
                    pass
                
                # [zaman, url, başlık, tarayıcı] formatına dönüştür
                history_entries = []
                for row in results:
                    visit_time, url, title = row
                    # Bazı URL'ler NULL başlığa sahip olabilir
                    if title is None:
                        title = "Başlık Yok"
                    history_entries.append((visit_time, url, title, "chrome"))
                
                self.last_fetch_time = datetime.now()
                return history_entries
                
            except Exception as e:
                print(f"Chrome geçmişi okunurken hata: {e}")
                try:
                    os.remove(temp_history)
                except:
                    pass
                return []
                
        except Exception as e:
            print(f"Chrome geçmişi alınırken hata: {e}")
            return []
        
    def _log_history_entries(self, entries):
        """
        Tarayıcı geçmişi girişlerini veritabanına kaydeder
        
        Args:
            entries: Ziyaret edilen sayfa kayıtları listesi
        """
        for timestamp, url, title, browser in entries:
            # ISO formatına dönüştür (eğer string değilse)
            if not isinstance(timestamp, str):
                timestamp_str = timestamp.isoformat()
            else:
                timestamp_str = timestamp
                
            # Veritabanına kaydet
            self.logger.log_browser_event(
                url=url,
                title=title,
                browser="chrome",
                timestamp=timestamp_str
            )
            
        # Kayıtlar işlendikten sonra, veritabanının güncellendiğinden emin olmak için commit yap
        try:
            if hasattr(self.logger, '_connect_db'):
                conn = self.logger._connect_db()
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Veritabanı commit işleminde hata: {e}")
            
    def _periodic_fetch(self):
        """Belirli aralıklarla tarayıcı geçmişini alır ve kaydeder"""
        while self.running:
            try:
                # Chrome geçmişini al
                new_entries = self._fetch_chrome_history()
                
                if new_entries:
                    entries_count = len(new_entries)
                    # Veritabanına kaydet
                    self._log_history_entries(new_entries)
                    
                    # Callback fonksiyonu varsa çağır
                    if self.callback:
                        try:
                            self.callback(entries_count)
                        except Exception as e:
                            print(f"Callback fonksiyonu çağrılırken hata: {e}")
                    else:
                        print(f"{entries_count} yeni Chrome geçmişi kaydı bulundu.")
                
                    # 2 saniye bekleyip Chrome'dan bir daha geçmişi kontrol et (güncellemeler için)
                    time.sleep(2)
                    self._fetch_chrome_history()
                    
            except Exception as e:
                print(f"Chrome geçmişi işlenirken hata: {e}")
                
            # Bir sonraki kontrole kadar bekle
            time.sleep(self.interval)
            
    def start_monitoring(self):
        """Tarayıcı geçmişi izlemeyi başlatır"""
        if self.running:
            return
            
        self.running = True
        self.last_fetch_time = None  # İlk çalıştırmada son 5 dakikayı kontrol etmek için None bırakıyoruz
        
        # İzleme thread'ini başlat
        fetch_thread = threading.Thread(target=self._periodic_fetch, daemon=True)
        fetch_thread.start()
        
        print(f"Chrome tarayıcısı izleyici başlatıldı. Kontrol aralığı: {self.interval} saniye")
        
        try:
            # Ana thread'in devam etmesi için bekle
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
            
    def stop_monitoring(self):
        """Tarayıcı geçmişi izlemeyi durdurur"""
        self.running = False
        print("Chrome tarayıcısı izleyici durduruldu.") 