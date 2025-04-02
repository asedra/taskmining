"""
Task Mining Prototype - Main Control Script
Bu script tüm sistemi başlatır ve kontrol eder.
"""

import os
import time
import threading
import sys
from event_listener import EventListener
from file_watcher import FileWatcher
from browser_log import BrowserLogger
from activity_logger import ActivityLogger
from analyzer import Analyzer

def setup_data_directory():
    """Veri dizinlerini oluştur"""
    os.makedirs("data/reports", exist_ok=True)

def main():
    print("Task Mining Prototype başlatılıyor...")
    
    # Dizinleri oluştur
    setup_data_directory()
    
    # Veritabanı bağlantısı oluştur
    logger = ActivityLogger("data/activity.db")
    
    # Analiz motoru oluştur
    analyzer = Analyzer(logger)
    
    # Yeni tarayıcı aktivitesi tespit edildiğinde rapor oluşturacak bir callback fonksiyonu
    def on_new_browser_entries(entries_count):
        if entries_count > 0:
            print(f"{entries_count} yeni Chrome geçmişi kaydı bulundu.")
            # Yeni kayıtlar geldiğinde hemen rapor oluştur
            analyzer.generate_daily_report()
    
    # Modülleri başlat
    event_listener = EventListener(logger)
    file_watcher = FileWatcher(logger, os.path.expanduser("~/Downloads"))
    browser_logger = BrowserLogger(logger, interval=10, callback=on_new_browser_entries)  # 10 saniyede bir kontrol et
    
    # Tüm izleyicileri ayrı threadlerde başlat
    threads = []
    
    event_thread = threading.Thread(target=event_listener.start_monitoring, daemon=True)
    file_thread = threading.Thread(target=file_watcher.start_monitoring, daemon=True)
    browser_thread = threading.Thread(target=browser_logger.start_monitoring, daemon=True)
    
    threads.extend([event_thread, file_thread, browser_thread])
    
    for thread in threads:
        thread.start()
    
    try:
        print("Kullanıcı aktiviteleri izleniyor. Durdurmak için Ctrl+C tuşlarına basın.")
        
        # Ana thread'in sonlanmaması için bekleme döngüsü
        while True:
            time.sleep(60)  # Her dakika kontrol et
            
            # Her dakika düzenli olarak haftalık raporu oluştur
            analyzer.generate_weekly_report()
            
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        print("İzleme durduruldu.")
        sys.exit(0)

if __name__ == "__main__":
    main() 