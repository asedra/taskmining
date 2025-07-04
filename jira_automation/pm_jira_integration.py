"""
PM Assistant - Jira Integration
==============================

PM Assistant ile Jira Windows Automation'ın entegre çalıştığı sistem.
PM Assistant'tan gelen fikirleri Jira task'larına dönüştürür ve mevcut task'ları takip eder.
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# PM Assistant'ı import et
sys.path.append('..')
try:
    from main_pm_assistant import PMAssistantIntegration
    from pm_assistant.models import ProjectIdea
except ImportError as e:
    print(f"PM Assistant import hatası: {e}")
    print("PM Assistant modüllerinin mevcut olduğundan emin olun")
    sys.exit(1)

# Jira Automation'ı import et
try:
    from jira_windows_automation import JiraWindowsAutomation
except ImportError as e:
    print(f"Jira Automation import hatası: {e}")
    print("jira_windows_automation.py dosyasının mevcut olduğundan emin olun")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pm_jira_integration.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PMJiraIntegration:
    """
    PM Assistant ile Jira Automation'ın entegre çalıştığı ana sınıf
    """
    
    def __init__(self, project_name: str = "PM-Jira-Integration"):
        self.project_name = project_name
        self.pm_assistant = PMAssistantIntegration(project_name)
        self.jira_automation = JiraWindowsAutomation()
        self.config_file = Path("pm_jira_config.json")
        self.task_mapping_file = Path("task_mapping.json")
        
        # Konfigürasyonu yükle
        self.config = self.load_config()
        self.task_mapping = self.load_task_mapping()
        
        logger.info(f"PM-Jira Integration başlatıldı: {project_name}")
    
    def load_config(self) -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükler"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info("PM-Jira konfigürasyon yüklendi")
                    return config
            except Exception as e:
                logger.error(f"Konfigürasyon yükleme hatası: {e}")
        
        # Varsayılan konfigürasyon
        return {
            "auto_sync": True,
            "default_project_key": "PROJ",
            "sync_interval_minutes": 30,
            "category_mapping": {
                "vision": "Epic",
                "scope": "Epic", 
                "deliverable": "Story",
                "milestone": "Story",
                "risk": "Task",
                "dependency": "Task"
            }
        }
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Konfigürasyonu dosyaya kaydeder"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info("PM-Jira konfigürasyon kaydedildi")
        except Exception as e:
            logger.error(f"Konfigürasyon kaydetme hatası: {e}")
    
    def load_task_mapping(self) -> Dict[str, Any]:
        """Task mapping dosyasını yükler"""
        if self.task_mapping_file.exists():
            try:
                with open(self.task_mapping_file, 'r', encoding='utf-8') as f:
                    mapping = json.load(f)
                    logger.info("Task mapping yüklendi")
                    return mapping
            except Exception as e:
                logger.error(f"Task mapping yükleme hatası: {e}")
        
        return {}
    
    def save_task_mapping(self, mapping: Dict[str, Any]) -> None:
        """Task mapping'i dosyaya kaydeder"""
        try:
            with open(self.task_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2, ensure_ascii=False)
            logger.info("Task mapping kaydedildi")
        except Exception as e:
            logger.error(f"Task mapping kaydetme hatası: {e}")
    
    def setup_jira_connection(self) -> bool:
        """Jira bağlantısını kurar"""
        try:
            print("Jira bağlantısı kuruluyor...")
            
            # Jira credentials al
            username, password = self.jira_automation.get_credentials()
            
            # Chrome'u başlat
            self.jira_automation.setup_chrome_driver()
            
            # Jira'ya giriş yap
            if self.jira_automation.login_to_jira():
                print("Jira bağlantısı başarıyla kuruldu!")
                logger.info("Jira bağlantısı kuruldu")
                return True
            else:
                print("Jira bağlantısı kurulamadı!")
                logger.error("Jira bağlantısı kurulamadı")
                return False
                
        except Exception as e:
            logger.error(f"Jira bağlantı hatası: {e}")
            print(f"Jira bağlantı hatası: {e}")
            return False
    
    def analyze_and_create_tasks(self, user_input: str, project_key: str = None) -> Dict[str, Any]:
        """
        Kullanıcı girişini analiz eder ve Jira'da task'lar oluşturur
        """
        try:
            print("Kullanıcı girişi analiz ediliyor...")
            
            # PM Assistant ile analiz yap
            analysis_result = self.pm_assistant.analyze_user_input(user_input)
            
            if analysis_result.get('ideas_generated', 0) == 0:
                print("Analiz sonucunda hiç task oluşturulmadı")
                return analysis_result
            
            # Jira bağlantısını kontrol et
            if not self.jira_automation.is_logged_in():
                print("Jira'ya giriş gerekli!")
                if not self.setup_jira_connection():
                    return analysis_result
            
            # Project key'i belirle
            if not project_key:
                project_key = self.config.get('default_project_key', 'PROJ')
            
            # PM Assistant'tan ideas al
            ideas = self.pm_assistant.pm_assistant.memory_manager.get_all_ideas(self.project_name)
            
            # Yeni ideas'ları (Jira ref'i olmayanları) Jira'ya aktar
            new_ideas = [idea for idea in ideas if not idea.jira_ref]
            
            created_tasks = []
            
            for idea in new_ideas:
                try:
                    # PMI kategori -> Jira Issue Type mapping
                    issue_type = self.config['category_mapping'].get(idea.category, 'Task')
                    
                    # Jira'da task oluştur
                    jira_key = self.jira_automation.create_task(
                        project_key=project_key,
                        summary=idea.summary,
                        description=f"{idea.description}\n\nKategori: {idea.category}\nÖncelik: {idea.priority}\nEtiketler: {', '.join(idea.tags)}",
                        issue_type=issue_type
                    )
                    
                    if jira_key:
                        # PM Assistant'ta Jira referansını güncelle
                        idea.jira_ref = jira_key
                        self.pm_assistant.pm_assistant.memory_manager.update_idea(idea)
                        
                        # Task mapping'e ekle
                        self.task_mapping[idea.id] = {
                            'jira_key': jira_key,
                            'pm_idea_id': idea.id,
                            'category': idea.category,
                            'created_at': datetime.now().isoformat(),
                            'status': 'created'
                        }
                        
                        created_tasks.append({
                            'pm_idea_id': idea.id,
                            'jira_key': jira_key,
                            'summary': idea.summary,
                            'category': idea.category,
                            'issue_type': issue_type
                        })
                        
                        print(f"✅ Task oluşturuldu: {jira_key} - {idea.summary}")
                        
                    else:
                        print(f"❌ Task oluşturulamadı: {idea.summary}")
                        
                except Exception as e:
                    logger.error(f"Task oluşturma hatası - {idea.id}: {e}")
                    print(f"❌ Task oluşturma hatası: {e}")
            
            # Task mapping'i kaydet
            self.save_task_mapping(self.task_mapping)
            
            # Sonuçları döndür
            result = analysis_result.copy()
            result['jira_tasks_created'] = len(created_tasks)
            result['created_tasks'] = created_tasks
            
            print(f"\n✅ Analiz tamamlandı: {len(created_tasks)} Jira task'ı oluşturuldu")
            
            return result
            
        except Exception as e:
            logger.error(f"Analiz ve task oluşturma hatası: {e}")
            print(f"Hata: {e}")
            return {'error': str(e)}
    
    def sync_jira_tasks_to_pm(self) -> List[Dict[str, Any]]:
        """
        Jira'daki task'ları PM Assistant'a senkronize eder
        """
        try:
            print("Jira task'ları PM Assistant'a senkronize ediliyor...")
            
            # Jira bağlantısını kontrol et
            if not self.jira_automation.is_logged_in():
                print("Jira'ya giriş gerekli!")
                if not self.setup_jira_connection():
                    return []
            
            # Jira'dan kullanıcının task'larını al
            jira_tasks = self.jira_automation.get_my_tasks()
            
            if not jira_tasks:
                print("Jira'da görev bulunamadı")
                return []
            
            synced_tasks = []
            
            for jira_task in jira_tasks:
                try:
                    jira_key = jira_task['key']
                    
                    # Bu task daha önce PM Assistant'a eklendi mi?
                    existing_mapping = None
                    for pm_id, mapping in self.task_mapping.items():
                        if mapping.get('jira_key') == jira_key:
                            existing_mapping = mapping
                            break
                    
                    if existing_mapping:
                        # Mevcut task'ı güncelle
                        existing_mapping['last_sync'] = datetime.now().isoformat()
                        existing_mapping['status'] = jira_task.get('status', 'Unknown')
                    else:
                        # Yeni task olarak PM Assistant'a ekle
                        idea = ProjectIdea(
                            id=f"jira_import_{jira_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            summary=jira_task['title'],
                            description=f"Jira'dan import edildi: {jira_task['url']}",
                            category='scope',  # Varsayılan kategori
                            priority=jira_task.get('priority', 'medium').lower(),
                            tags=['jira-import'],
                            jira_ref=jira_key
                        )
                        
                        # PM Assistant'a kaydet
                        self.pm_assistant.pm_assistant.memory_manager.store_idea(idea, self.project_name)
                        
                        # Task mapping'e ekle
                        self.task_mapping[idea.id] = {
                            'jira_key': jira_key,
                            'pm_idea_id': idea.id,
                            'category': 'scope',
                            'imported_at': datetime.now().isoformat(),
                            'status': jira_task.get('status', 'Unknown'),
                            'source': 'jira_import'
                        }
                        
                        synced_tasks.append({
                            'jira_key': jira_key,
                            'pm_idea_id': idea.id,
                            'title': jira_task['title'],
                            'status': jira_task.get('status', 'Unknown'),
                            'action': 'imported'
                        })
                        
                        print(f"📥 Task import edildi: {jira_key} - {jira_task['title']}")
                    
                except Exception as e:
                    logger.error(f"Task senkronizasyon hatası - {jira_task['key']}: {e}")
                    print(f"❌ Task senkronizasyon hatası: {e}")
            
            # Task mapping'i kaydet
            self.save_task_mapping(self.task_mapping)
            
            print(f"✅ Senkronizasyon tamamlandı: {len(synced_tasks)} task import edildi")
            
            return synced_tasks
            
        except Exception as e:
            logger.error(f"Jira-PM senkronizasyon hatası: {e}")
            print(f"Senkronizasyon hatası: {e}")
            return []
    
    def get_task_status_report(self) -> Dict[str, Any]:
        """
        Task durumu raporu oluşturur
        """
        try:
            # PM Assistant'tan tüm ideas'ları al
            pm_ideas = self.pm_assistant.pm_assistant.memory_manager.get_all_ideas(self.project_name)
            
            # Jira task'larını al (eğer bağlıysa)
            jira_tasks = []
            if self.jira_automation.driver and self.jira_automation.is_logged_in():
                jira_tasks = self.jira_automation.get_my_tasks()
            
            # İstatistikleri hesapla
            total_ideas = len(pm_ideas)
            ideas_with_jira = len([idea for idea in pm_ideas if idea.jira_ref])
            ideas_without_jira = total_ideas - ideas_with_jira
            
            category_breakdown = {}
            for idea in pm_ideas:
                if idea.category not in category_breakdown:
                    category_breakdown[idea.category] = {'total': 0, 'with_jira': 0}
                category_breakdown[idea.category]['total'] += 1
                if idea.jira_ref:
                    category_breakdown[idea.category]['with_jira'] += 1
            
            # Raporu oluştur
            report = {
                'project_name': self.project_name,
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_pm_ideas': total_ideas,
                    'ideas_with_jira': ideas_with_jira,
                    'ideas_without_jira': ideas_without_jira,
                    'total_jira_tasks': len(jira_tasks),
                    'sync_percentage': round((ideas_with_jira / total_ideas * 100) if total_ideas > 0 else 0, 2)
                },
                'category_breakdown': category_breakdown,
                'task_mapping_count': len(self.task_mapping),
                'last_sync': max([mapping.get('last_sync', mapping.get('created_at', '')) 
                                for mapping in self.task_mapping.values()] or ['Never'])
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Rapor oluşturma hatası: {e}")
            return {'error': str(e)}
    
    def run_interactive_mode(self):
        """Etkileşimli mod çalıştırır"""
        print("=== PM Assistant - Jira Integration ===")
        print(f"Proje: {self.project_name}")
        
        while True:
            print("\n=== Ana Menü ===")
            print("1. Proje fikirlerini analiz et ve Jira task'ları oluştur")
            print("2. Jira task'larını PM Assistant'a senkronize et")
            print("3. Task durumu raporunu görüntüle")
            print("4. Jira Dashboard'u aç")
            print("5. PM Assistant raporu oluştur")
            print("6. Konfigürasyon ayarları")
            print("7. Çıkış")
            
            choice = input("\nSeçiminizi yapın (1-7): ").strip()
            
            if choice == '1':
                print("\n=== Proje Fikirlerini Analiz Et ===")
                user_input = input("Proje fikirlerinizi, gereksinimlerinizi veya hedeflerinizi yazın:\n")
                
                if user_input.strip():
                    project_key = input("Jira proje anahtarını girin (varsayılan: PROJ): ").strip()
                    if not project_key:
                        project_key = self.config.get('default_project_key', 'PROJ')
                    
                    # Jira bağlantısını kur
                    if not self.setup_jira_connection():
                        print("Jira bağlantısı kurulamadı!")
                        continue
                    
                    result = self.analyze_and_create_tasks(user_input, project_key)
                    
                    if 'error' not in result:
                        print(f"\n✅ Analiz tamamlandı!")
                        print(f"   - {result.get('ideas_generated', 0)} fikir oluşturuldu")
                        print(f"   - {result.get('jira_tasks_created', 0)} Jira task'ı oluşturuldu")
                    
                else:
                    print("Geçersiz giriş!")
            
            elif choice == '2':
                print("\n=== Jira Task'larını Senkronize Et ===")
                
                # Jira bağlantısını kur
                if not self.setup_jira_connection():
                    print("Jira bağlantısı kurulamadı!")
                    continue
                
                synced_tasks = self.sync_jira_tasks_to_pm()
                
                if synced_tasks:
                    print(f"\n✅ {len(synced_tasks)} task senkronize edildi")
                    for task in synced_tasks:
                        print(f"   - {task['jira_key']}: {task['title']}")
                else:
                    print("Senkronize edilecek yeni task bulunamadı")
            
            elif choice == '3':
                print("\n=== Task Durumu Raporu ===")
                report = self.get_task_status_report()
                
                if 'error' not in report:
                    print(f"\nProje: {report['project_name']}")
                    print(f"Tarih: {report['generated_at']}")
                    print("\n📊 Özet:")
                    print(f"   - Toplam PM Fikirleri: {report['summary']['total_pm_ideas']}")
                    print(f"   - Jira Task'ı Olan: {report['summary']['ideas_with_jira']}")
                    print(f"   - Jira Task'ı Olmayan: {report['summary']['ideas_without_jira']}")
                    print(f"   - Senkronizasyon Oranı: %{report['summary']['sync_percentage']}")
                    
                    print("\n📋 Kategori Dağılımı:")
                    for category, stats in report['category_breakdown'].items():
                        print(f"   - {category.title()}: {stats['with_jira']}/{stats['total']} Jira'da")
                else:
                    print(f"Rapor oluşturma hatası: {report['error']}")
            
            elif choice == '4':
                print("\n=== Jira Dashboard ===")
                
                # Jira bağlantısını kur
                if not self.setup_jira_connection():
                    print("Jira bağlantısı kurulamadı!")
                    continue
                
                self.jira_automation.open_jira_dashboard()
                print("Jira Dashboard tarayıcıda açıldı")
            
            elif choice == '5':
                print("\n=== PM Assistant Raporu ===")
                report_path = self.pm_assistant.generate_project_report()
                print(f"Rapor oluşturuldu: {report_path}")
            
            elif choice == '6':
                print("\n=== Konfigürasyon Ayarları ===")
                print("1. Varsayılan proje anahtarını değiştir")
                print("2. Otomatik senkronizasyonu aç/kapat")
                print("3. Kategori-Issue Type eşleştirmesini görüntüle")
                
                config_choice = input("Seçiminizi yapın (1-3): ").strip()
                
                if config_choice == '1':
                    new_key = input(f"Yeni proje anahtarı (şuan: {self.config.get('default_project_key', 'PROJ')}): ").strip()
                    if new_key:
                        self.config['default_project_key'] = new_key
                        self.save_config(self.config)
                        print("Proje anahtarı güncellendi")
                
                elif config_choice == '2':
                    current = self.config.get('auto_sync', True)
                    self.config['auto_sync'] = not current
                    self.save_config(self.config)
                    print(f"Otomatik senkronizasyon: {'Açık' if self.config['auto_sync'] else 'Kapalı'}")
                
                elif config_choice == '3':
                    print("\nKategori → Issue Type Eşleştirmesi:")
                    for category, issue_type in self.config['category_mapping'].items():
                        print(f"   - {category} → {issue_type}")
            
            elif choice == '7':
                break
            
            else:
                print("Geçersiz seçim!")
        
        # Cleanup
        print("\nÇıkış yapılıyor...")
        if self.jira_automation.driver:
            self.jira_automation.close_browser()
        print("İyi günler!")

def main():
    """Ana fonksiyon"""
    print("PM Assistant - Jira Integration başlatılıyor...")
    
    # Proje adını al
    project_name = input("Proje adını girin (varsayılan: PM-Jira-Integration): ").strip()
    if not project_name:
        project_name = "PM-Jira-Integration"
    
    integration = PMJiraIntegration(project_name)
    
    try:
        integration.run_interactive_mode()
    except KeyboardInterrupt:
        print("\n\nProgram kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"Genel hata: {e}")
        print(f"Beklenmeyen hata: {e}")
    finally:
        if integration.jira_automation.driver:
            integration.jira_automation.close_browser()

if __name__ == "__main__":
    main()