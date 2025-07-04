"""
Jira Windows Automation
======================

Windows ortamında Chrome üzerinden Jira'ya otomatik bağlantı ve task yönetimi.
Şifre yönetimi ve otomatik giriş özelliği ile.
"""

import os
import sys
import time
import json
import getpass
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Selenium bulunamadı! Kurulum için: pip install selenium")
    sys.exit(1)

# Şifre güvenliği için keyring
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    print("Keyring bulunamadı! Kurulum için: pip install keyring")
    KEYRING_AVAILABLE = False

import logging

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jira_automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class JiraWindowsAutomation:
    """
    Windows ortamında Jira otomasyonu için ana sınıf
    """
    
    def __init__(self):
        self.driver = None
        self.jira_url = None
        self.username = None
        self.password = None
        self.config_file = Path("jira_config.json")
        self.chrome_path = self._find_chrome_path()
        
        logger.info("Jira Windows Automation başlatıldı")
    
    def _find_chrome_path(self) -> str:
        """Chrome'un Windows'taki yolunu bulur"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USER'))
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Chrome bulundu: {path}")
                return path
        
        logger.warning("Chrome bulunamadı! Varsayılan path kullanılacak")
        return "chrome"
    
    def load_config(self) -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükler"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("Konfigürasyon yüklendi")
                    return config
            except Exception as e:
                logger.error(f"Konfigürasyon yükleme hatası: {e}")
        
        return {}
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Konfigürasyonu dosyaya kaydeder"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info("Konfigürasyon kaydedildi")
        except Exception as e:
            logger.error(f"Konfigürasyon kaydetme hatası: {e}")
    
    def get_credentials(self) -> tuple:
        """Kullanıcı bilgilerini alır (ilk seferde sorar, sonra kaydedileni kullanır)"""
        config = self.load_config()
        
        # Jira URL'ini al
        if 'jira_url' in config:
            self.jira_url = config['jira_url']
            print(f"Kayıtlı Jira URL: {self.jira_url}")
        else:
            self.jira_url = input("Jira URL'inizi girin (örn: https://yourcompany.atlassian.net): ").strip()
            if not self.jira_url.startswith('http'):
                self.jira_url = 'https://' + self.jira_url
            config['jira_url'] = self.jira_url
        
        # Kullanıcı adını al
        if 'username' in config:
            self.username = config['username']
            print(f"Kayıtlı kullanıcı: {self.username}")
        else:
            self.username = input("Jira kullanıcı adınızı girin: ").strip()
            config['username'] = self.username
        
        # Şifreyi al
        password_key = f"jira_password_{self.username}"
        
        if KEYRING_AVAILABLE:
            # Keyring'den şifreyi al
            saved_password = keyring.get_password("jira_automation", password_key)
            if saved_password:
                self.password = saved_password
                print("Kayıtlı şifre kullanılacak")
            else:
                self.password = getpass.getpass("Jira şifrenizi girin: ")
                # Şifreyi kaydet
                save_password = input("Şifrenizi kaydetmek istiyor musunuz? (y/n): ").lower().strip()
                if save_password in ['y', 'yes', 'evet', 'e']:
                    keyring.set_password("jira_automation", password_key, self.password)
                    print("Şifre güvenli olarak kaydedildi")
        else:
            # Keyring yoksa basit dosya kaydı (güvenli değil, sadece demo için)
            self.password = getpass.getpass("Jira şifrenizi girin: ")
            logger.warning("Keyring mevcut değil, şifre kaydedilmeyecek")
        
        # Konfigürasyonu kaydet
        self.save_config(config)
        
        return self.username, self.password
    
    def setup_chrome_driver(self) -> webdriver.Chrome:
        """Chrome WebDriver'ı ayarlar"""
        chrome_options = Options()
        
        # Chrome ayarları
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Kullanıcı profili (oturum açık kalması için)
        user_data_dir = Path.home() / "jira_automation_chrome_profile"
        user_data_dir.mkdir(exist_ok=True)
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        try:
            # Chrome binary path'i ayarla
            if self.chrome_path != "chrome":
                chrome_options.binary_location = self.chrome_path
            
            # WebDriver'ı başlat
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome WebDriver başlatıldı")
            return self.driver
            
        except Exception as e:
            logger.error(f"Chrome WebDriver başlatma hatası: {e}")
            print(f"Chrome WebDriver hatası: {e}")
            print("ChromeDriver'ın kurulu olduğundan emin olun: https://chromedriver.chromium.org/")
            raise
    
    def login_to_jira(self) -> bool:
        """Jira'ya giriş yapar"""
        try:
            print("Jira'ya giriş yapılıyor...")
            
            # Jira'ya git
            self.driver.get(self.jira_url)
            time.sleep(3)
            
            # Zaten giriş yapılmış mı kontrol et
            if self.is_logged_in():
                print("Zaten Jira'ya giriş yapılmış!")
                return True
            
            # Giriş sayfasını bekle
            wait = WebDriverWait(self.driver, 10)
            
            try:
                # Kullanıcı adı alanını bul ve doldur
                username_field = wait.until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                username_field.clear()
                username_field.send_keys(self.username)
                
                # Continue/İleri butonuna tıkla
                continue_btn = self.driver.find_element(By.ID, "login-submit")
                continue_btn.click()
                
                time.sleep(2)
                
                # Şifre alanını bul ve doldur
                password_field = wait.until(
                    EC.presence_of_element_located((By.ID, "password"))
                )
                password_field.clear()
                password_field.send_keys(self.password)
                
                # Giriş butonuna tıkla
                login_btn = self.driver.find_element(By.ID, "login-submit")
                login_btn.click()
                
                # Giriş sonrasını bekle
                time.sleep(5)
                
                # Giriş kontrolü
                if self.is_logged_in():
                    print("Jira'ya başarıyla giriş yapıldı!")
                    logger.info("Jira'ya başarıyla giriş yapıldı")
                    return True
                else:
                    print("Giriş başarısız! Kullanıcı adı veya şifre hatalı olabilir.")
                    logger.error("Jira girişi başarısız")
                    return False
                    
            except TimeoutException:
                print("Giriş sayfası elementleri bulunamadı!")
                logger.error("Jira giriş sayfası elementleri bulunamadı")
                return False
                
        except Exception as e:
            logger.error(f"Jira giriş hatası: {e}")
            print(f"Jira giriş hatası: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """Jira'ya giriş yapılıp yapılmadığını kontrol eder"""
        try:
            # Dashboard veya profil menüsünün varlığını kontrol et
            elements_to_check = [
                "//div[@id='header']",
                "//nav[@role='navigation']",
                "//a[@data-help-id='header.user.menu']",
                "//button[@aria-label='Your profile and settings']"
            ]
            
            for xpath in elements_to_check:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    if element.is_displayed():
                        return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Giriş kontrolü hatası: {e}")
            return False
    
    def open_jira_dashboard(self) -> bool:
        """Jira dashboard'unu açar"""
        try:
            if not self.is_logged_in():
                print("Önce Jira'ya giriş yapmalısınız!")
                return False
            
            # Dashboard'a git
            dashboard_url = f"{self.jira_url}/secure/Dashboard.jspa"
            self.driver.get(dashboard_url)
            
            # Sayfanın yüklenmesini bekle
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            print("Jira Dashboard açıldı")
            logger.info("Jira Dashboard açıldı")
            return True
            
        except Exception as e:
            logger.error(f"Dashboard açma hatası: {e}")
            print(f"Dashboard açma hatası: {e}")
            return False
    
    def get_my_tasks(self) -> List[Dict[str, Any]]:
        """Kullanıcının görevlerini getirir"""
        try:
            if not self.is_logged_in():
                print("Önce Jira'ya giriş yapmalısınız!")
                return []
            
            # "Assigned to me" filterine git
            filter_url = f"{self.jira_url}/issues/?jql=assignee=currentuser()AND resolution=Unresolved"
            self.driver.get(filter_url)
            
            # Sayfanın yüklenmesini bekle
            time.sleep(3)
            
            tasks = []
            try:
                # Issue listesini bul
                wait = WebDriverWait(self.driver, 10)
                
                # Farklı olası selektörler
                issue_selectors = [
                    "//div[@class='issue-table']//tr[contains(@class, 'issuerow')]",
                    "//ol[@class='issue-list']//li",
                    "//div[contains(@class, 'issue-list')]//div[contains(@class, 'issue')]"
                ]
                
                issues = []
                for selector in issue_selectors:
                    try:
                        issues = self.driver.find_elements(By.XPATH, selector)
                        if issues:
                            break
                    except NoSuchElementException:
                        continue
                
                if not issues:
                    print("Görev bulunamadı veya sayfa henüz yüklenmemiş")
                    return []
                
                for issue in issues[:10]:  # İlk 10 görevi al
                    try:
                        # Issue key'ini bul
                        key_element = issue.find_element(By.XPATH, ".//a[contains(@class, 'issue-link')]")
                        key = key_element.text.strip()
                        
                        # Issue title'ını bul
                        title_element = issue.find_element(By.XPATH, ".//span[contains(@class, 'summary')]")
                        title = title_element.text.strip()
                        
                        # Issue status'unu bul
                        try:
                            status_element = issue.find_element(By.XPATH, ".//span[contains(@class, 'status')]")
                            status = status_element.text.strip()
                        except NoSuchElementException:
                            status = "Bilinmiyor"
                        
                        # Issue priority'sini bul
                        try:
                            priority_element = issue.find_element(By.XPATH, ".//img[contains(@alt, 'Priority')]")
                            priority = priority_element.get_attribute('alt')
                        except NoSuchElementException:
                            priority = "Bilinmiyor"
                        
                        task = {
                            'key': key,
                            'title': title,
                            'status': status,
                            'priority': priority,
                            'url': f"{self.jira_url}/browse/{key}"
                        }
                        
                        tasks.append(task)
                        
                    except Exception as e:
                        logger.warning(f"Görev ayrıştırma hatası: {e}")
                        continue
                
                logger.info(f"{len(tasks)} görev bulundu")
                return tasks
                
            except TimeoutException:
                print("Görev listesi yüklenemedi")
                logger.error("Görev listesi timeout")
                return []
                
        except Exception as e:
            logger.error(f"Görev getirme hatası: {e}")
            print(f"Görev getirme hatası: {e}")
            return []
    
    def open_task(self, task_key: str) -> bool:
        """Belirli bir görevi açar"""
        try:
            if not self.is_logged_in():
                print("Önce Jira'ya giriş yapmalısınız!")
                return False
            
            # Görev URL'ini oluştur ve aç
            task_url = f"{self.jira_url}/browse/{task_key}"
            self.driver.get(task_url)
            
            # Sayfanın yüklenmesini bekle
            time.sleep(3)
            
            print(f"Görev {task_key} açıldı")
            logger.info(f"Görev {task_key} açıldı")
            return True
            
        except Exception as e:
            logger.error(f"Görev açma hatası: {e}")
            print(f"Görev açma hatası: {e}")
            return False
    
    def create_task(self, project_key: str, summary: str, description: str = "", 
                   issue_type: str = "Task") -> Optional[str]:
        """Yeni görev oluşturur"""
        try:
            if not self.is_logged_in():
                print("Önce Jira'ya giriş yapmalısınız!")
                return None
            
            # Create issue sayfasına git
            create_url = f"{self.jira_url}/secure/CreateIssue.jspa"
            self.driver.get(create_url)
            
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, 10)
            
            # Project seçimi
            try:
                project_field = wait.until(
                    EC.element_to_be_clickable((By.ID, "project-field"))
                )
                project_field.click()
                
                # Project arama
                project_input = self.driver.find_element(By.ID, "project-field")
                project_input.clear()
                project_input.send_keys(project_key)
                time.sleep(1)
                
                # İlk sonucu seç
                first_result = self.driver.find_element(By.XPATH, "//div[contains(@class, 'suggestions')]//li[1]")
                first_result.click()
                
            except Exception as e:
                print(f"Project seçimi hatası: {e}")
                return None
            
            # Issue type seçimi
            try:
                issue_type_field = self.driver.find_element(By.ID, "issuetype-field")
                issue_type_field.click()
                
                # Issue type arama
                issue_type_input = self.driver.find_element(By.ID, "issuetype-field")
                issue_type_input.clear()
                issue_type_input.send_keys(issue_type)
                time.sleep(1)
                
                # İlk sonucu seç
                first_result = self.driver.find_element(By.XPATH, "//div[contains(@class, 'suggestions')]//li[1]")
                first_result.click()
                
            except Exception as e:
                print(f"Issue type seçimi hatası: {e}")
                return None
            
            # Summary (başlık)
            try:
                summary_field = self.driver.find_element(By.ID, "summary")
                summary_field.clear()
                summary_field.send_keys(summary)
            except Exception as e:
                print(f"Summary girme hatası: {e}")
                return None
            
            # Description (açıklama)
            if description:
                try:
                    description_field = self.driver.find_element(By.ID, "description")
                    description_field.clear()
                    description_field.send_keys(description)
                except Exception as e:
                    print(f"Description girme hatası: {e}")
            
            # Create butonuna tıkla
            try:
                create_btn = self.driver.find_element(By.ID, "create-issue-submit")
                create_btn.click()
                
                time.sleep(3)
                
                # Oluşturulan issue'nun key'ini al
                try:
                    issue_key_element = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "issue-link"))
                    )
                    issue_key = issue_key_element.text.strip()
                    
                    print(f"Görev başarıyla oluşturuldu: {issue_key}")
                    logger.info(f"Görev oluşturuldu: {issue_key}")
                    return issue_key
                    
                except TimeoutException:
                    print("Görev oluşturuldu ancak key alınamadı")
                    return "CREATED"
                    
            except Exception as e:
                print(f"Create butonu hatası: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Görev oluşturma hatası: {e}")
            print(f"Görev oluşturma hatası: {e}")
            return None
    
    def close_browser(self):
        """Tarayıcıyı kapatır"""
        if self.driver:
            self.driver.quit()
            logger.info("Tarayıcı kapatıldı")
    
    def run_interactive_mode(self):
        """Etkileşimli mod çalıştırır"""
        print("=== Jira Windows Otomasyonu ===")
        print("1. Kurulum ve giriş yapılıyor...")
        
        # Credentials al
        username, password = self.get_credentials()
        
        # Chrome'u başlat
        try:
            self.setup_chrome_driver()
        except Exception as e:
            print(f"Chrome başlatma hatası: {e}")
            return
        
        # Jira'ya giriş yap
        if not self.login_to_jira():
            print("Jira'ya giriş yapılamadı!")
            self.close_browser()
            return
        
        # Dashboard'u aç
        self.open_jira_dashboard()
        
        # Interaktif menü
        while True:
            print("\n=== Jira Otomasyonu Menüsü ===")
            print("1. Görevlerimi göster")
            print("2. Görev aç")
            print("3. Yeni görev oluştur")
            print("4. Dashboard'u aç")
            print("5. Çıkış")
            
            choice = input("\nSeçiminizi yapın (1-5): ").strip()
            
            if choice == '1':
                print("\nGörevleriniz yükleniyor...")
                tasks = self.get_my_tasks()
                
                if tasks:
                    print(f"\n{len(tasks)} görev bulundu:")
                    for i, task in enumerate(tasks, 1):
                        print(f"{i}. {task['key']} - {task['title']} [{task['status']}]")
                else:
                    print("Görev bulunamadı")
            
            elif choice == '2':
                task_key = input("Açmak istediğiniz görev anahtarını girin (örn: PROJ-123): ").strip()
                if task_key:
                    self.open_task(task_key)
                    print(f"Görev {task_key} tarayıcıda açıldı")
            
            elif choice == '3':
                project_key = input("Proje anahtarını girin (örn: PROJ): ").strip()
                summary = input("Görev başlığını girin: ").strip()
                description = input("Görev açıklamasını girin (opsiyonel): ").strip()
                
                if project_key and summary:
                    created_key = self.create_task(project_key, summary, description)
                    if created_key:
                        print(f"Görev oluşturuldu: {created_key}")
                    else:
                        print("Görev oluşturulamadı")
                else:
                    print("Proje anahtarı ve başlık gerekli!")
            
            elif choice == '4':
                self.open_jira_dashboard()
                print("Dashboard açıldı")
            
            elif choice == '5':
                break
            
            else:
                print("Geçersiz seçim!")
        
        # Cleanup
        input("\nÇıkmak için Enter'a basın...")
        self.close_browser()

def main():
    """Ana fonksiyon"""
    automation = JiraWindowsAutomation()
    
    try:
        automation.run_interactive_mode()
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"Genel hata: {e}")
        print(f"Beklenmeyen hata: {e}")
    finally:
        automation.close_browser()

if __name__ == "__main__":
    main()