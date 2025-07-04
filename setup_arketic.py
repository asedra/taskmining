#!/usr/bin/env python3
"""
Arketic Assistant Setup Script
Bu script Arketic Assistant'ın kurulum ve yapılandırma işlemlerini otomatikleştirir.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

class ArketicSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.required_files = [
            "arketic_assistant.py",
            "activity_logger.py",
            "analyzer.py",
            "event_listener.py",
            "file_watcher.py",
            "browser_log.py",
            "requirements.txt"
        ]
        
    def print_header(self, title):
        """Başlık yazdırma"""
        print("\n" + "="*60)
        print(f"🚀 {title}")
        print("="*60)
        
    def print_step(self, step_num, title):
        """Adım başlığı yazdırma"""
        print(f"\n📋 Adım {step_num}: {title}")
        print("-" * 40)
        
    def check_python_version(self):
        """Python versiyonunu kontrol et"""
        self.print_step(1, "Python Versiyonu Kontrolü")
        
        version = sys.version_info
        print(f"Python versiyonu: {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            print("❌ Python 3.7 veya üzeri gerekli!")
            print("Lütfen Python'u güncellyin: https://python.org/downloads")
            return False
        
        print("✅ Python versiyonu uygun")
        return True
        
    def check_required_files(self):
        """Gerekli dosyaları kontrol et"""
        self.print_step(2, "Gerekli Dosyalar Kontrolü")
        
        missing_files = []
        for file in self.required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print("❌ Eksik dosyalar bulundu:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        
        print("✅ Tüm gerekli dosyalar mevcut")
        return True
        
    def install_dependencies(self):
        """Bağımlılıkları yükle"""
        self.print_step(3, "Bağımlılıklar Yükleniyor")
        
        try:
            # requirements.txt dosyasını kontrol et
            req_file = self.project_root / "requirements.txt"
            if not req_file.exists():
                print("❌ requirements.txt dosyası bulunamadı")
                return False
            
            # Bağımlılıkları yükle
            print("📦 Bağımlılıklar yükleniyor...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(req_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Bağımlılık yükleme hatası:")
                print(result.stderr)
                return False
            
            print("✅ Bağımlılıklar başarıyla yüklendi")
            return True
            
        except Exception as e:
            print(f"❌ Bağımlılık yükleme hatası: {e}")
            return False
            
    def create_directories(self):
        """Gerekli dizinleri oluştur"""
        self.print_step(4, "Dizin Yapısı Oluşturma")
        
        directories = [
            "data",
            "data/reports",
            "data/temp",
            "utils"
        ]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  📁 {dir_name} dizini oluşturuldu")
            except Exception as e:
                print(f"  ❌ {dir_name} dizini oluşturulamadı: {e}")
                
        print("✅ Dizin yapısı hazırlandı")
        
    def create_config_file(self):
        """Yapılandırma dosyası oluştur"""
        self.print_step(5, "Yapılandırma Dosyası Oluşturma")
        
        config_file = self.project_root / "arketic_config.json"
        
        # Mevcut config dosyasını kontrol et
        if config_file.exists():
            overwrite = input("📋 Mevcut config dosyası var. Üzerine yazılsın mı? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("  ℹ️ Config dosyası korundu")
                return True
        
        # Varsayılan config oluştur
        default_config = {
            "database": {
                "path": "data/arketic_activity.db"
            },
            "monitoring": {
                "file_watch_paths": [
                    "~/Downloads",
                    "~/Documents",
                    "~/Desktop"
                ],
                "browser_check_interval": 10,
                "report_generation_interval": 300
            },
            "reports": {
                "output_dir": "data/reports",
                "formats": ["json", "html", "csv"],
                "daily_auto_generate": True,
                "weekly_auto_generate": True
            },
            "automation": {
                "min_sequence_frequency": 3,
                "analysis_days": 7,
                "threshold_app_usage_minutes": 30
            },
            "logging": {
                "level": "INFO",
                "file": "data/arketic.log"
            },
            "privacy": {
                "mask_sensitive_data": True,
                "data_retention_days": 30
            }
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ Config dosyası oluşturuldu: {config_file}")
            return True
            
        except Exception as e:
            print(f"  ❌ Config dosyası oluşturulamadı: {e}")
            return False
            
    def create_utils_file(self):
        """Yardımcı dosya oluştur"""
        self.print_step(6, "Yardımcı Dosyalar Oluşturma")
        
        utils_dir = self.project_root / "utils"
        time_utils_file = utils_dir / "time_utils.py"
        
        if not time_utils_file.exists():
            time_utils_content = '''"""
Zaman işlemleri için yardımcı fonksiyonlar
"""

from datetime import datetime, timezone
import time

def get_current_timestamp():
    """Şu anki zaman damgasını ISO 8601 formatında döndürür"""
    return datetime.now(timezone.utc).isoformat()

def get_current_date():
    """Şu anki tarihi YYYY-MM-DD formatında döndürür"""
    return datetime.now().strftime("%Y-%m-%d")

def format_duration(seconds):
    """Saniye cinsinden süreyi HH:MM:SS formatında döndürür"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def timestamp_to_datetime(timestamp_str):
    """ISO 8601 timestamp'i datetime objesine çevirir"""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        return datetime.now()
'''
            
            try:
                with open(time_utils_file, 'w', encoding='utf-8') as f:
                    f.write(time_utils_content)
                print(f"  ✅ time_utils.py oluşturuldu")
            except Exception as e:
                print(f"  ❌ time_utils.py oluşturulamadı: {e}")
        
        # __init__.py dosyası oluştur
        init_file = utils_dir / "__init__.py"
        if not init_file.exists():
            try:
                init_file.touch()
                print(f"  ✅ utils/__init__.py oluşturuldu")
            except Exception as e:
                print(f"  ❌ utils/__init__.py oluşturulamadı: {e}")
                
        print("✅ Yardımcı dosyalar hazırlandı")
        
    def test_installation(self):
        """Kurulumu test et"""
        self.print_step(7, "Kurulum Testi")
        
        try:
            # Arketic Assistant'ı import etmeyi dene
            sys.path.insert(0, str(self.project_root))
            
            print("  🔍 Modül import testi...")
            from arketic_assistant import ArketicAssistant
            
            print("  🔍 Assistant başlatma testi...")
            assistant = ArketicAssistant()
            
            print("  🔍 Veritabanı bağlantı testi...")
            assistant.activity_logger._connect_db().close()
            
            print("✅ Kurulum testi başarılı")
            return True
            
        except Exception as e:
            print(f"❌ Kurulum testi başarısız: {e}")
            return False
            
    def create_shortcuts(self):
        """Kısayol scriptleri oluştur"""
        self.print_step(8, "Kısayol Scriptleri")
        
        # Başlatma scripti
        start_script = self.project_root / "start_arketic.py"
        start_content = '''#!/usr/bin/env python3
"""Arketic Assistant başlatma scripti"""
import sys
import os

# Proje dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arketic_assistant import ArketicAssistant

if __name__ == "__main__":
    assistant = ArketicAssistant()
    assistant.interactive_mode()
'''
        
        try:
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(start_content)
            
            # Executable yapın (Linux/Mac)
            if os.name != 'nt':
                os.chmod(start_script, 0o755)
            
            print(f"  ✅ Başlatma scripti: {start_script}")
            
        except Exception as e:
            print(f"  ❌ Başlatma scripti oluşturulamadı: {e}")
            
    def show_completion_message(self):
        """Tamamlanma mesajı göster"""
        self.print_header("Kurulum Tamamlandı! 🎉")
        
        print("🚀 Arketic Assistant kullanıma hazır!")
        print("\n📋 Kullanım Komutları:")
        print("  • İnteraktif mod: python arketic_assistant.py")
        print("  • Hızlı başlatma: python start_arketic.py")
        print("  • Demo: python arketic_demo.py")
        print("  • Komut satırı: python arketic_assistant.py --help")
        
        print("\n📁 Önemli Dosyalar:")
        print("  • Yapılandırma: arketic_config.json")
        print("  • Veritabanı: data/arketic_activity.db")
        print("  • Raporlar: data/reports/")
        print("  • Loglar: data/arketic.log")
        
        print("\n🔧 Sorun giderme için:")
        print("  • Logları kontrol edin: data/arketic.log")
        print("  • Dokümantasyon: ARKETIC_ASSISTANT_README.md")
        
        print("\n✨ İyi kullanımlar!")
        
    def run_setup(self):
        """Kurulum sürecini başlat"""
        self.print_header("Arketic Assistant Kurulum")
        
        print("Bu script Arketic Assistant'ı kurup yapılandıracak.")
        input("Devam etmek için Enter'a basın...")
        
        # Kurulum adımları
        steps = [
            ("Python versiyonu kontrolü", self.check_python_version),
            ("Gerekli dosyalar kontrolü", self.check_required_files),
            ("Bağımlılıklar yükleme", self.install_dependencies),
            ("Dizin yapısı oluşturma", self.create_directories),
            ("Yapılandırma dosyası", self.create_config_file),
            ("Yardımcı dosyalar", self.create_utils_file),
            ("Kurulum testi", self.test_installation),
            ("Kısayol scriptleri", self.create_shortcuts)
        ]
        
        failed_steps = []
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    failed_steps.append(step_name)
                    print(f"⚠️ {step_name} adımı başarısız")
            except Exception as e:
                failed_steps.append(step_name)
                print(f"❌ {step_name} adımında hata: {e}")
        
        # Sonuçları göster
        if failed_steps:
            print("\n⚠️ Bazı adımlar başarısız oldu:")
            for step in failed_steps:
                print(f"  - {step}")
            print("\nManuel olarak düzeltmeniz gerekebilir.")
        else:
            self.show_completion_message()

def main():
    """Ana fonksiyon"""
    setup = ArketicSetup()
    
    try:
        setup.run_setup()
    except KeyboardInterrupt:
        print("\n\n⏹️ Kurulum iptal edildi.")
    except Exception as e:
        print(f"\n❌ Kurulum hatası: {e}")
        print("Lütfen manuel kurulum yapın.")

if __name__ == "__main__":
    main()