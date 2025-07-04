#!/usr/bin/env python3
"""
Arketic Assistant - Comprehensive Task Mining Assistant
Bu assistant, kullanıcıların günlük bilgisayar aktivitelerini izler, analiz eder ve 
otomasyon önerileri sunar. Tüm task mining işlevlerini tek bir assistant altında toplar.
"""

import os
import sys
import json
import time
import threading
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import argparse

# Task mining bileşenlerini import et
from activity_logger import ActivityLogger
from analyzer import Analyzer
from event_listener import EventListener
from file_watcher import FileWatcher
from browser_log import BrowserLogger

class ArketicAssistant:
    """
    Arketic Assistant - Kapsamlı Task Mining Asistanı
    
    Bu sınıf, kullanıcı aktivitelerini izlemek, analiz etmek ve
    otomasyon önerileri sunmak için gerekli tüm fonksiyonları içerir.
    """
    
    def __init__(self, config_file: str = "arketic_config.json"):
        """
        Arketic Assistant'ı başlatır
        
        Args:
            config_file: Yapılandırma dosyası yolu
        """
        self.config = self._load_config(config_file)
        self.setup_logging()
        self.setup_directories()
        
        # Core components
        self.activity_logger = ActivityLogger(self.config["database"]["path"])
        self.analyzer = Analyzer(self.activity_logger)
        
        # Monitoring components
        self.event_listener = None
        self.file_watcher = None
        self.browser_logger = None
        
        # Control flags
        self.is_monitoring = False
        self.monitoring_threads = []
        
        logging.info("Arketic Assistant başlatıldı")
    
    def _load_config(self, config_file: str) -> Dict:
        """Yapılandırma dosyasını yükler"""
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
                "report_generation_interval": 60
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
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge with default config
                    self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"Yapılandırma dosyası yüklenirken hata: {e}")
                print("Varsayılan yapılandırma kullanılıyor...")
        
        return default_config
    
    def _merge_config(self, base: Dict, update: Dict):
        """Yapılandırma dosyalarını birleştirir"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def setup_logging(self):
        """Logging sistemini kurar"""
        log_level = getattr(logging, self.config["logging"]["level"].upper())
        log_file = self.config["logging"]["file"]
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def setup_directories(self):
        """Gerekli dizinleri oluşturur"""
        directories = [
            os.path.dirname(self.config["database"]["path"]),
            self.config["reports"]["output_dir"],
            "data/temp"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def start_monitoring(self):
        """Tüm izleme bileşenlerini başlatır"""
        if self.is_monitoring:
            logging.warning("İzleme zaten başlatılmış")
            return
        
        logging.info("Arketic Assistant izleme moduna geçiyor...")
        
        # Browser monitoring callback
        def on_browser_activity(count):
            if count > 0:
                logging.info(f"{count} yeni tarayıcı aktivitesi tespit edildi")
                if self.config["reports"]["daily_auto_generate"]:
                    self.generate_daily_report()
        
        # Initialize monitoring components
        self.event_listener = EventListener(self.activity_logger)
        self.browser_logger = BrowserLogger(
            self.activity_logger,
            interval=self.config["monitoring"]["browser_check_interval"],
            callback=on_browser_activity
        )
        
        # File watchers for multiple paths
        self.file_watchers = []
        for path in self.config["monitoring"]["file_watch_paths"]:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                watcher = FileWatcher(self.activity_logger, expanded_path)
                self.file_watchers.append(watcher)
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self.event_listener.start_monitoring, daemon=True),
            threading.Thread(target=self.browser_logger.start_monitoring, daemon=True)
        ]
        
        for watcher in self.file_watchers:
            threads.append(
                threading.Thread(target=watcher.start_monitoring, daemon=True)
            )
        
        # Report generation thread
        if self.config["reports"]["weekly_auto_generate"]:
            threads.append(
                threading.Thread(target=self._periodic_report_generation, daemon=True)
            )
        
        self.monitoring_threads = threads
        for thread in threads:
            thread.start()
        
        self.is_monitoring = True
        logging.info("Tüm izleme bileşenleri başlatıldı")
    
    def stop_monitoring(self):
        """İzleme işlemini durdurur"""
        if not self.is_monitoring:
            logging.warning("İzleme zaten durdurulmuş")
            return
        
        logging.info("İzleme durdruluyor...")
        self.is_monitoring = False
        
        # Monitoring bileşenlerini durdur
        if self.event_listener:
            self.event_listener.stop_monitoring()
        if self.browser_logger:
            self.browser_logger.stop_monitoring()
        for watcher in getattr(self, 'file_watchers', []):
            watcher.stop_monitoring()
        
        logging.info("İzleme durduruldu")
    
    def _periodic_report_generation(self):
        """Periyodik rapor oluşturma"""
        while self.is_monitoring:
            try:
                time.sleep(self.config["monitoring"]["report_generation_interval"])
                if self.config["reports"]["weekly_auto_generate"]:
                    self.generate_weekly_report()
            except Exception as e:
                logging.error(f"Periyodik rapor oluşturulurken hata: {e}")
    
    def generate_daily_report(self) -> Optional[str]:
        """Günlük rapor oluşturur"""
        try:
            self.analyzer.generate_daily_report()
            report_path = os.path.join(
                self.config["reports"]["output_dir"],
                f"daily_report_{date.today().strftime('%Y-%m-%d')}.json"
            )
            logging.info(f"Günlük rapor oluşturuldu: {report_path}")
            return report_path
        except Exception as e:
            logging.error(f"Günlük rapor oluşturulurken hata: {e}")
            return None
    
    def generate_weekly_report(self) -> Optional[str]:
        """Haftalık rapor oluşturur"""
        try:
            self.analyzer.generate_weekly_report()
            report_path = os.path.join(
                self.config["reports"]["output_dir"],
                f"weekly_report_{date.today().strftime('%Y-%m-%d')}.json"
            )
            logging.info(f"Haftalık rapor oluşturuldu: {report_path}")
            return report_path
        except Exception as e:
            logging.error(f"Haftalık rapor oluşturulurken hata: {e}")
            return None
    
    def get_activity_summary(self, days: int = 1) -> Dict:
        """Aktivite özetini getirir"""
        try:
            summary = {
                "app_usage": self.analyzer.analyze_app_usage(),
                "browser_patterns": self.analyzer.analyze_browser_patterns(days=days),
                "file_activities": self.analyzer.analyze_file_activities(days=days),
                "automation_candidates": self.analyzer.identify_automation_candidates()
            }
            return summary
        except Exception as e:
            logging.error(f"Aktivite özeti alınırken hata: {e}")
            return {}
    
    def get_automation_recommendations(self) -> List[Dict]:
        """Otomasyon önerilerini getirir"""
        try:
            candidates = self.analyzer.identify_automation_candidates()
            
            # Önerileri skorla ve sırala
            scored_recommendations = []
            for candidate in candidates:
                score = self._calculate_automation_score(candidate)
                recommendation = {
                    "recommendation": candidate,
                    "score": score,
                    "priority": self._get_priority_level(score)
                }
                scored_recommendations.append(recommendation)
            
            # Skora göre sırala
            scored_recommendations.sort(key=lambda x: x["score"], reverse=True)
            
            return scored_recommendations
        except Exception as e:
            logging.error(f"Otomasyon önerileri alınırken hata: {e}")
            return []
    
    def _calculate_automation_score(self, candidate: Dict) -> float:
        """Otomasyon adayı için skor hesaplar"""
        score = 0.0
        
        if candidate["type"] == "sequence":
            # Sıklık bazlı skor
            score = candidate["frequency"] * 10
        elif candidate["type"] == "app_usage":
            # Süre bazlı skor (dakika olarak)
            duration_parts = candidate["duration"].split(":")
            if len(duration_parts) == 3:
                hours, minutes, seconds = map(int, duration_parts)
                total_minutes = hours * 60 + minutes + seconds / 60
                score = total_minutes / 10  # Her 10 dakika = 1 puan
        elif candidate["type"] == "file_activity":
            # Aktivite sayısı bazlı skor
            score = candidate["count"] / 5  # Her 5 aktivite = 1 puan
        
        return min(score, 100.0)  # Maksimum 100 puan
    
    def _get_priority_level(self, score: float) -> str:
        """Skor bazlı öncelik seviyesi belirler"""
        if score >= 50:
            return "Yüksek"
        elif score >= 20:
            return "Orta"
        else:
            return "Düşük"
    
    def export_data(self, format: str = "json", days: int = 7) -> Optional[str]:
        """Verileri dışa aktarır"""
        try:
            export_data = {
                "export_date": datetime.now().isoformat(),
                "period_days": days,
                "summary": self.get_activity_summary(days),
                "recommendations": self.get_automation_recommendations(),
                "raw_data": {
                    "user_events": self.activity_logger.get_user_events(limit=1000),
                    "file_events": self.activity_logger.get_file_events(limit=500),
                    "browser_events": self.activity_logger.get_browser_events(limit=500)
                }
            }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"arketic_export_{timestamp}.{format}"
            filepath = os.path.join(self.config["reports"]["output_dir"], filename)
            
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            elif format == "csv":
                # CSV export için pandas kullan
                try:
                    import pandas as pd  # type: ignore
                    # Basit CSV için sadece özet bilgileri
                    summary_df = pd.DataFrame([export_data["summary"]])
                    summary_df.to_csv(filepath, index=False)
                except ImportError:
                    logging.warning("Pandas mevcut değil, CSV export JSON olarak kaydedildi")
                    with open(filepath.replace('.csv', '.json'), 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                    filepath = filepath.replace('.csv', '.json')
            
            logging.info(f"Veriler dışa aktarıldı: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"Veri dışa aktarılırken hata: {e}")
            return None
    
    def interactive_mode(self):
        """İnteraktif mod başlatır"""
        print("\n" + "="*50)
        print("🤖 Arketic Assistant - İnteraktif Mod")
        print("="*50)
        
        while True:
            print("\n📋 Mevcut Komutlar:")
            print("1. İzlemeyi başlat")
            print("2. İzlemeyi durdur")
            print("3. Günlük rapor oluştur")
            print("4. Haftalık rapor oluştur")
            print("5. Aktivite özeti göster")
            print("6. Otomasyon önerileri göster")
            print("7. Verileri dışa aktar")
            print("8. Durumu kontrol et")
            print("9. Çıkış")
            
            try:
                choice = input("\n🔢 Seçiminiz (1-9): ").strip()
                
                if choice == "1":
                    self.start_monitoring()
                elif choice == "2":
                    self.stop_monitoring()
                elif choice == "3":
                    path = self.generate_daily_report()
                    if path:
                        print(f"✅ Günlük rapor oluşturuldu: {path}")
                elif choice == "4":
                    path = self.generate_weekly_report()
                    if path:
                        print(f"✅ Haftalık rapor oluşturuldu: {path}")
                elif choice == "5":
                    summary = self.get_activity_summary()
                    print("\n📊 Aktivite Özeti:")
                    print(json.dumps(summary, indent=2, ensure_ascii=False))
                elif choice == "6":
                    recommendations = self.get_automation_recommendations()
                    print("\n🔄 Otomasyon Önerileri:")
                    for i, rec in enumerate(recommendations[:5], 1):
                        print(f"{i}. {rec['recommendation']['description']}")
                        print(f"   Skor: {rec['score']:.1f}, Öncelik: {rec['priority']}")
                elif choice == "7":
                    format_choice = input("Format (json/csv): ").strip().lower()
                    days = int(input("Kaç günlük veri (varsayılan 7): ") or "7")
                    path = self.export_data(format_choice, days)
                    if path:
                        print(f"✅ Veriler dışa aktarıldı: {path}")
                elif choice == "8":
                    status = "🟢 Aktif" if self.is_monitoring else "🔴 Pasif"
                    print(f"\n📊 İzleme Durumu: {status}")
                    print(f"📁 Veritabanı: {self.config['database']['path']}")
                    print(f"📂 Rapor Dizini: {self.config['reports']['output_dir']}")
                elif choice == "9":
                    print("👋 Görüşürüz!")
                    if self.is_monitoring:
                        self.stop_monitoring()
                    break
                else:
                    print("❌ Geçersiz seçim!")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Görüşürüz!")
                if self.is_monitoring:
                    self.stop_monitoring()
                break
            except Exception as e:
                print(f"❌ Hata: {e}")

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="Arketic Assistant - Task Mining Asistanı")
    parser.add_argument("--config", default="arketic_config.json", help="Yapılandırma dosyası")
    parser.add_argument("--start", action="store_true", help="İzlemeyi başlat")
    parser.add_argument("--interactive", action="store_true", help="İnteraktif mod")
    parser.add_argument("--report", choices=["daily", "weekly"], help="Rapor oluştur")
    parser.add_argument("--export", choices=["json", "csv"], help="Verileri dışa aktar")
    parser.add_argument("--days", type=int, default=7, help="Analiz günü sayısı")
    
    args = parser.parse_args()
    
    # Arketic Assistant'ı başlat
    assistant = ArketicAssistant(args.config)
    
    try:
        if args.interactive:
            assistant.interactive_mode()
        elif args.start:
            assistant.start_monitoring()
            print("İzleme başlatıldı. Durdurmak için Ctrl+C tuşlarına basın.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nİzleme durduruldu.")
        elif args.report:
            if args.report == "daily":
                assistant.generate_daily_report()
            elif args.report == "weekly":
                assistant.generate_weekly_report()
        elif args.export:
            assistant.export_data(args.export, args.days)
        else:
            # Varsayılan olarak interaktif mod
            assistant.interactive_mode()
            
    except Exception as e:
        logging.error(f"Uygulama çalışırken hata: {e}")
        sys.exit(1)
    finally:
        if assistant.is_monitoring:
            assistant.stop_monitoring()

if __name__ == "__main__":
    main()