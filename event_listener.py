"""
Pencere değişikliklerini ve klavye/fare aktivitelerini izler
"""

import time
import threading
import pygetwindow as gw
from pynput import keyboard, mouse
import win32gui
import win32process
import psutil
import datetime
import os
from PIL import ImageGrab
from utils.time_utils import get_current_timestamp

class EventListener:
    def __init__(self, activity_logger):
        """
        Olay dinleyicisini başlatır
        
        Args:
            activity_logger: Aktiviteleri kaydedecek ActivityLogger nesnesi
        """
        self.logger = activity_logger
        self.running = False
        self.active_window = {"title": "", "application": "", "last_update": None}
        self.last_input_time = None
        self.lock = threading.Lock()
        self.screenshot_dir = "data/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    def _get_active_window_info(self):
        """
        Aktif pencerenin başlığını ve uygulama adını alır
        
        Returns:
            tuple: (window_title, application_name)
        """
        try:
            # Aktif pencere tanıtıcısını al
            hwnd = win32gui.GetForegroundWindow()
            
            # Pencere başlığını al
            window_title = win32gui.GetWindowText(hwnd)
            
            # Pencereye ait işlem ID'sini al
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            # İşlem adını al
            try:
                process = psutil.Process(process_id)
                application = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                application = "Bilinmeyen Uygulama"
                
            return window_title, application
            
        except Exception as e:
            print(f"Pencere bilgisi alınırken hata: {e}")
            return "Hata", "Hata"
            
    def _on_window_change(self, window_title, application):
        """Pencere değişikliği olayını işler"""
        with self.lock:
            # Yeni pencere bilgisini kaydet
            self.logger.log_user_event(
                window_title=window_title,
                application=application,
                event_type="window_change"
            )
            
            # Önceki aktif pencere için kullanım süresini güncelle
            if self.active_window["last_update"]:
                elapsed_time = (datetime.datetime.now() - self.active_window["last_update"]).total_seconds()
                if elapsed_time > 0 and self.active_window["application"]:
                    # Uygulama kullanım süresini güncelle
                    self.logger.update_app_usage(
                        application=self.active_window["application"],
                        duration_seconds=int(elapsed_time)
                    )
            
            # Yeni aktif pencere bilgilerini kaydet
            self.active_window = {
                "title": window_title,
                "application": application,
                "last_update": datetime.datetime.now()
            }
            
    def _take_screenshot(self, event_type, event_details):
        """
        Ekran görüntüsü alır ve kaydeder
        
        Args:
            event_type: Olay türü (keyboard, mouse_click)
            event_details: Olay detayları
            
        Returns:
            tuple: (ekran görüntüsü dosya yolu, dosya adı)
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{event_type}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            print(f"Ekran görüntüsü alınıyor: {filepath}")
            
            # Ekran görüntüsü al
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            print(f"Ekran görüntüsü başarıyla kaydedildi: {filepath}")
            return filepath, filename
        except Exception as e:
            print(f"Ekran görüntüsü alınırken hata: {e}")
            return None, None

    def _on_key_press(self, key):
        """Klavye tuşu basma olayını işler"""
        with self.lock:
            try:
                # Son aktivite zamanını güncelle
                self.last_input_time = datetime.datetime.now()
                
                # Aktif pencere bilgilerini kontrol et ve güncelle
                window_title, application = self._get_active_window_info()
                
                print(f"Klavye olayı tespit edildi - Pencere: {window_title}, Uygulama: {application}")
                
                # Klavye olayını kaydet
                try:
                    key_char = key.char if hasattr(key, 'char') else str(key)
                    # Bazı tuşlar özel kullanımlar için maskelenebilir
                    if key_char.isalnum():
                        masked_key = key_char  # Alfanumerik tuşlar güvenli
                    else:
                        masked_key = "[SPECIAL_KEY]"  # Özel tuşları maskeleyebiliriz
                    
                    # Ekran görüntüsü al
                    screenshot_path, screenshot_filename = self._take_screenshot("keyboard", masked_key)
                    
                    print(f"Klavye olayı kaydediliyor: {masked_key}")
                    self.logger.log_user_event(
                        window_title=window_title,
                        application=application,
                        event_type="keyboard",
                        event_details=masked_key,
                        screenshot_path=screenshot_path,
                        screenshot_filename=screenshot_filename
                    )
                    print("Klavye olayı başarıyla kaydedildi")
                except AttributeError:
                    # Özel tuşlar için
                    screenshot_path, screenshot_filename = self._take_screenshot("keyboard", "[SPECIAL_KEY]")
                    print("Özel tuş olayı kaydediliyor")
                    self.logger.log_user_event(
                        window_title=window_title,
                        application=application,
                        event_type="keyboard",
                        event_details="[SPECIAL_KEY]",
                        screenshot_path=screenshot_path,
                        screenshot_filename=screenshot_filename
                    )
                    print("Özel tuş olayı başarıyla kaydedildi")
            except Exception as e:
                print(f"Klavye olayı işlenirken hata: {e}")
                
    def _on_mouse_click(self, x, y, button, pressed):
        """Fare tıklama olayını işler"""
        if pressed:  # Sadece basma olayını izle, bırakma olayını değil
            with self.lock:
                try:
                    # Son aktivite zamanını güncelle
                    self.last_input_time = datetime.datetime.now()
                    
                    # Aktif pencere bilgilerini kontrol et ve güncelle
                    window_title, application = self._get_active_window_info()
                    
                    print(f"Fare tıklaması tespit edildi - Pencere: {window_title}, Uygulama: {application}")
                    
                    # Ekran görüntüsü al
                    event_details = f"button={button}, position=({x}, {y})"
                    screenshot_path, screenshot_filename = self._take_screenshot("mouse_click", event_details)
                    
                    print(f"Fare tıklaması kaydediliyor: {event_details}")
                    # Fare olayını kaydet
                    self.logger.log_user_event(
                        window_title=window_title,
                        application=application,
                        event_type="mouse_click",
                        event_details=event_details,
                        screenshot_path=screenshot_path,
                        screenshot_filename=screenshot_filename
                    )
                    print("Fare tıklaması başarıyla kaydedildi")
                except Exception as e:
                    print(f"Fare tıklaması işlenirken hata: {e}")

    def _check_active_window(self):
        """Belirli aralıklarla aktif pencere değişikliklerini kontrol eder"""
        while self.running:
            try:
                current_title, current_app = self._get_active_window_info()
                
                # Pencere değişikliği varsa kaydet
                if (current_title != self.active_window["title"] or 
                    current_app != self.active_window["application"]):
                    self._on_window_change(current_title, current_app)
                # Pencere aynı kaldıysa ve aktif ise kullanım süresini güncelle
                elif self.last_input_time and (datetime.datetime.now() - self.last_input_time).total_seconds() < 60:
                    # Eğer son 60 saniye içinde aktivite olduysa, uygulamanın aktif olduğunu varsay
                    with self.lock:
                        self.active_window["last_update"] = datetime.datetime.now()
            except Exception as e:
                print(f"Aktif pencere kontrolünde hata: {e}")
                
            time.sleep(1)  # Her 1 saniyede bir kontrol et
            
    def _update_app_usage_periodically(self):
        """Belirli aralıklarla uygulama kullanım sürelerini günceller"""
        while self.running:
            with self.lock:
                # Aktif pencerenin son güncellenme zamanını kontrol et
                if self.active_window["last_update"]:
                    elapsed_time = (datetime.datetime.now() - self.active_window["last_update"]).total_seconds()
                    
                    # Son giriş zamanını kontrol et (kullanıcı aktif mi?)
                    is_active = (self.last_input_time and 
                                 (datetime.datetime.now() - self.last_input_time).total_seconds() < 60)
                    
                    if is_active and elapsed_time > 0 and self.active_window["application"]:
                        # Uygulama kullanım süresini güncelle
                        self.logger.update_app_usage(
                            application=self.active_window["application"],
                            duration_seconds=int(elapsed_time)
                        )
                        # Son güncelleme zamanını güncelle
                        self.active_window["last_update"] = datetime.datetime.now()
                        
            time.sleep(30)  # Her 30 saniyede bir güncelle
            
    def start_monitoring(self):
        """Tüm izleme işlemlerini başlatır"""
        if self.running:
            return
            
        self.running = True
        
        # Aktif pencere kontrolünü başlat
        window_thread = threading.Thread(target=self._check_active_window, daemon=True)
        window_thread.start()
        
        # Uygulama kullanım süresi güncelleme işlemini başlat
        usage_thread = threading.Thread(target=self._update_app_usage_periodically, daemon=True)
        usage_thread.start()
        
        # Klavye dinleyicisini başlat
        keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        keyboard_listener.daemon = True
        keyboard_listener.start()
        
        # Fare dinleyicisini başlat
        mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        mouse_listener.daemon = True
        mouse_listener.start()
        
        print("Etkinlik dinleyicisi başlatıldı.")
        
        try:
            # Ana thread'in devam etmesi için bekle
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()
            
    def stop_monitoring(self):
        """Tüm izleme işlemlerini durdurur"""
        self.running = False
        print("Etkinlik dinleyicisi durduruldu.") 