"""
Dosya sistemi değişikliklerini izler
"""

import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileEventHandler(FileSystemEventHandler):
    """Dosya sistemi olaylarını işler"""
    
    def __init__(self, activity_logger):
        """
        Args:
            activity_logger: Aktivite kaydedici
        """
        self.logger = activity_logger
        
    def on_created(self, event):
        """Dosya oluşturma olayını işler"""
        if not event.is_directory:
            self.logger.log_file_event(
                file_path=event.src_path,
                event_type="created"
            )
            
    def on_deleted(self, event):
        """Dosya silme olayını işler"""
        if not event.is_directory:
            self.logger.log_file_event(
                file_path=event.src_path,
                event_type="deleted"
            )
            
    def on_modified(self, event):
        """Dosya düzenleme olayını işler"""
        if not event.is_directory:
            self.logger.log_file_event(
                file_path=event.src_path,
                event_type="modified"
            )
            
    def on_moved(self, event):
        """Dosya taşıma olayını işler"""
        if not event.is_directory:
            self.logger.log_file_event(
                file_path=f"{event.src_path} -> {event.dest_path}",
                event_type="moved"
            )

class FileWatcher:
    """Belirli dizinleri izlemek için kullanılır"""
    
    def __init__(self, activity_logger, path=None):
        """
        Args:
            activity_logger: Aktivite kaydedici
            path: İzlenecek dizin yolu (varsayılan: Downloads)
        """
        self.logger = activity_logger
        
        if path is None:
            self.path = os.path.expanduser("~/Downloads")
        else:
            self.path = path
            
        self.event_handler = FileEventHandler(activity_logger)
        self.observer = Observer()
        self.running = False
        
    def start_monitoring(self):
        """Dosya sistemi izlemeyi başlatır"""
        if self.running:
            return
            
        # Dizinin varlığını kontrol et
        if not os.path.exists(self.path):
            print(f"Uyarı: İzlenecek dizin {self.path} bulunamadı.")
            return
            
        # İzleyiciyi başlat
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        self.running = True
        
        print(f"Dosya izleyici başlatıldı. İzlenen dizin: {self.path}")
        
        try:
            # Ana thread'in devam etmesi için bekle
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
            
    def stop_monitoring(self):
        """Dosya sistemi izlemeyi durdurur"""
        if not self.running:
            return
            
        self.observer.stop()
        self.observer.join()
        self.running = False
        
        print("Dosya izleyici durduruldu.") 