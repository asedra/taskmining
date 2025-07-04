"""
Jira Windows Automation - Kurulum ve Test
========================================

Windows ortamında Jira otomasyonu için kurulum, test ve başlatma scripti.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Python versiyonunu kontrol eder"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 veya üzeri gerekli!")
        print(f"Şu anki versiyon: {sys.version}")
        return False
    
    print(f"✅ Python versiyonu: {sys.version}")
    return True

def install_dependencies():
    """Gerekli kütüphaneleri kurar"""
    print("\n=== Bağımlılıklar Kuruluyor ===")
    
    requirements = [
        "selenium>=4.0.0",
        "keyring>=23.0.0", 
        "webdriver-manager>=3.8.0"
    ]
    
    for req in requirements:
        try:
            print(f"Kuruluyor: {req}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ {req} kuruldu")
        except subprocess.CalledProcessError as e:
            print(f"❌ {req} kurulamadı: {e}")
            return False
    
    return True

def download_chromedriver():
    """ChromeDriver'ı otomatik indirir"""
    try:
        print("\n=== ChromeDriver Kontrol Ediliyor ===")
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        
        # ChromeDriver'ı indir ve kur
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver hazır: {driver_path}")
        
        # Test et
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(driver_path, options=options)
        driver.quit()
        
        print("✅ ChromeDriver testi başarılı")
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver kurulum hatası: {e}")
        print("Manuel kurulum: https://chromedriver.chromium.org/")
        return False

def find_chrome():
    """Chrome'un kurulu olup olmadığını kontrol eder"""
    print("\n=== Chrome Kontrol Ediliyor ===")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome bulundu: {path}")
            return True
    
    print("❌ Chrome bulunamadı!")
    print("Chrome'u indirin: https://www.google.com/chrome/")
    return False

def create_sample_config():
    """Örnek konfigürasyon dosyası oluşturur"""
    print("\n=== Konfigürasyon Dosyası Oluşturuluyor ===")
    
    config = {
        "jira_url": "https://yourcompany.atlassian.net",
        "username": "your-email@domain.com",
        "auto_sync": True,
        "default_project_key": "PROJ",
        "category_mapping": {
            "vision": "Epic",
            "scope": "Epic",
            "deliverable": "Story", 
            "milestone": "Story",
            "risk": "Task",
            "dependency": "Task"
        }
    }
    
    config_file = Path("jira_config_template.json")
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Örnek konfigürasyon oluşturuldu: {config_file}")
        print("Bu dosyayı düzenleyerek kendi ayarlarınızı yapabilirsiniz")
        return True
        
    except Exception as e:
        print(f"❌ Konfigürasyon dosyası oluşturulamadı: {e}")
        return False

def test_basic_functionality():
    """Temel fonksiyonaliteyi test eder"""
    print("\n=== Temel Test ===")
    
    try:
        # Selenium test
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        
        if "Google" in driver.title:
            print("✅ Selenium Chrome testi başarılı")
        else:
            print("❌ Selenium Chrome testi başarısız")
            
        driver.quit()
        
        # Keyring test
        import keyring
        print("✅ Keyring kütüphanesi hazır")
        
        return True
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

def create_startup_script():
    """Başlatma scripti oluşturur"""
    print("\n=== Başlatma Scripti Oluşturuluyor ===")
    
    startup_script = """@echo off
title Jira Windows Automation
echo === Jira Windows Automation ===
echo.

REM Python yolunu kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo Python bulunamadi! Python 3.7+ kurmaniz gerekiyor.
    pause
    exit /b 1
)

REM Ana scripti calistir
echo Jira Windows Automation baslatiliyor...
echo.
python pm_jira_integration.py

pause
"""
    
    try:
        startup_file = Path("start_jira_automation.bat")
        with open(startup_file, 'w', encoding='utf-8') as f:
            f.write(startup_script)
        
        print(f"✅ Başlatma scripti oluşturuldu: {startup_file}")
        print("Bu dosyaya çift tıklayarak programı başlatabilirsiniz")
        return True
        
    except Exception as e:
        print(f"❌ Başlatma scripti oluşturulamadı: {e}")
        return False

def main():
    """Ana kurulum fonksiyonu"""
    print("=== Jira Windows Automation Kurulum ===")
    print("Bu script gerekli kurulumları yapacak ve sistemi test edecek\n")
    
    success_count = 0
    total_steps = 6
    
    # Adım 1: Python versiyon kontrolü
    if check_python_version():
        success_count += 1
    
    # Adım 2: Chrome kontrolü
    if find_chrome():
        success_count += 1
    
    # Adım 3: Bağımlılık kurulumu
    if install_dependencies():
        success_count += 1
    
    # Adım 4: ChromeDriver kurulumu
    if download_chromedriver():
        success_count += 1
    
    # Adım 5: Konfigürasyon dosyası
    if create_sample_config():
        success_count += 1
    
    # Adım 6: Temel test
    if test_basic_functionality():
        success_count += 1
    
    # Başlatma scripti (bonus)
    create_startup_script()
    
    # Sonuç
    print(f"\n=== Kurulum Sonucu ===")
    print(f"Başarılı adımlar: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("🎉 Kurulum başarıyla tamamlandı!")
        print("\nSonraki adımlar:")
        print("1. jira_config_template.json dosyasını düzenleyin")
        print("2. python pm_jira_integration.py komutuyla başlatın")
        print("3. Veya start_jira_automation.bat dosyasına çift tıklayın")
    else:
        print("⚠️ Bazı adımlar başarısız oldu. Lütfen hataları kontrol edin.")
        
        if success_count >= 4:
            print("\nTemel kurulum tamamlandı, program çalışabilir")
            print("Hataları görmezden gelerek devam edebilirsiniz")

def test_integration():
    """PM Assistant entegrasyonunu test eder"""
    print("\n=== PM Assistant Entegrasyon Testi ===")
    
    try:
        # PM Assistant modüllerini test et
        sys.path.append('..')
        
        from main_pm_assistant import PMAssistantIntegration
        from pm_assistant.models import ProjectIdea
        
        print("✅ PM Assistant modülleri başarıyla import edildi")
        
        # Test PM Assistant
        pm = PMAssistantIntegration("Test-Project")
        print("✅ PM Assistant başlatıldı")
        
        return True
        
    except ImportError as e:
        print(f"❌ PM Assistant import hatası: {e}")
        print("PM Assistant modüllerinin mevcut olduğundan emin olun")
        return False
    except Exception as e:
        print(f"❌ PM Assistant test hatası: {e}")
        return False

def run_quick_demo():
    """Hızlı demo çalıştırır"""
    print("\n=== Hızlı Demo ===")
    
    demo_input = """
    Bir e-ticaret platformu geliştirmek istiyoruz.
    Kritik özellikler: kullanıcı girişi, ürün kataloğu, sepet yönetimi.
    Güvenlik çok önemli - ödeme sistemi güvenliği sağlanmalı.
    6 ay içinde tamamlanması hedefleniyor.
    """
    
    try:
        # PM Assistant'la analiz
        from main_pm_assistant import PMAssistantIntegration
        
        pm = PMAssistantIntegration("Demo-Project")
        result = pm.analyze_user_input(demo_input)
        
        print(f"✅ Demo analiz tamamlandı")
        print(f"   - {result.get('ideas_generated', 0)} fikir oluşturuldu")
        print(f"   - {len(result.get('suggested_actions', []))} öneri")
        
        # Oluşturulan fikirleri göster
        ideas = pm.pm_assistant.memory_manager.get_all_ideas("Demo-Project")
        if ideas:
            print("\n📋 Oluşturulan Fikirler:")
            for idea in ideas[:3]:  # İlk 3 fikri göster
                print(f"   - {idea.summary} [{idea.category}]")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo hatası: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test-integration":
            test_integration()
        elif sys.argv[1] == "--demo":
            run_quick_demo()
        elif sys.argv[1] == "--test-all":
            main()
            test_integration()
            run_quick_demo()
        else:
            print("Kullanım:")
            print("python setup_jira_automation.py          # Normal kurulum")
            print("python setup_jira_automation.py --test-integration  # PM Assistant testi")
            print("python setup_jira_automation.py --demo             # Hızlı demo")
            print("python setup_jira_automation.py --test-all         # Tüm testler")
    else:
        main()