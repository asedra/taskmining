#!/usr/bin/env python3
"""
Arketic Assistant Demo Script
Bu script Arketic Assistant'ın temel özelliklerini demonstre eder.
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta

# Arketic Assistant'ı import et
try:
    from arketic_assistant import ArketicAssistant
except ImportError:
    print("❌ Arketic Assistant modülü bulunamadı!")
    print("Lütfen aynı dizinde arketic_assistant.py dosyasının bulunduğundan emin olun.")
    sys.exit(1)

def print_header(title):
    """Başlık yazdırma fonksiyonu"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_section(title):
    """Bölüm başlığı yazdırma fonksiyonu"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_configuration():
    """Yapılandırma sistemini demonstre eder"""
    print_header("Arketic Assistant Yapılandırma Demo")
    
    # Demo konfigürasyonu oluştur
    demo_config = {
        "database": {
            "path": "demo_data/arketic_demo.db"
        },
        "monitoring": {
            "file_watch_paths": [
                "~/Downloads",
                "~/Documents"
            ],
            "browser_check_interval": 5,
            "report_generation_interval": 30
        },
        "reports": {
            "output_dir": "demo_data/reports",
            "formats": ["json", "csv"],
            "daily_auto_generate": True,
            "weekly_auto_generate": False
        },
        "automation": {
            "min_sequence_frequency": 2,
            "analysis_days": 3,
            "threshold_app_usage_minutes": 15
        },
        "logging": {
            "level": "INFO",
            "file": "demo_data/arketic_demo.log"
        }
    }
    
    # Demo config dosyasını oluştur
    config_file = "arketic_demo_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(demo_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Demo yapılandırma dosyası oluşturuldu: {config_file}")
    print(f"📁 Demo veritabanı yolu: {demo_config['database']['path']}")
    print(f"📊 Demo rapor dizini: {demo_config['reports']['output_dir']}")
    
    return config_file

def demo_assistant_initialization(config_file):
    """Assistant başlatma demonstrasyonu"""
    print_header("Arketic Assistant Başlatma Demo")
    
    try:
        # Assistant'ı başlat
        assistant = ArketicAssistant(config_file)
        print("✅ Arketic Assistant başarıyla başlatıldı!")
        
        # Yapılandırma bilgilerini göster
        print_section("Yapılandırma Bilgileri")
        print(f"📁 Veritabanı: {assistant.config['database']['path']}")
        print(f"📊 Rapor Dizini: {assistant.config['reports']['output_dir']}")
        print(f"🔍 İzleme Aralığı: {assistant.config['monitoring']['browser_check_interval']} saniye")
        
        return assistant
        
    except Exception as e:
        print(f"❌ Assistant başlatılırken hata: {e}")
        return None

def demo_monitoring_simulation(assistant):
    """İzleme simülasyonu"""
    print_header("İzleme Simülasyonu")
    
    if not assistant:
        print("❌ Assistant başlatılamadı, simülasyon atlanıyor.")
        return
    
    print("🔄 İzleme simülasyonu başlatılıyor...")
    print("(Gerçek izleme yerine demo verileri oluşturuluyor)")
    
    # Simülasyon verileri
    demo_apps = ["chrome.exe", "vscode.exe", "notepad.exe", "excel.exe"]
    demo_activities = ["window_change", "keyboard", "mouse_click"]
    demo_files = ["document.pdf", "data.xlsx", "notes.txt"]
    
    # Demo aktiviteler oluştur
    print_section("Demo Aktiviteler Oluşturuluyor")
    
    for i in range(10):
        # Rastgele demo aktivite
        app = demo_apps[i % len(demo_apps)]
        activity = demo_activities[i % len(demo_activities)]
        
        # Aktiviteyi kaydet
        assistant.activity_logger.log_user_event(
            window_title=f"Demo Window {i+1}",
            application=app,
            event_type=activity,
            event_details=f"Demo aktivite {i+1}"
        )
        
        # Uygulama kullanımını kaydet
        assistant.activity_logger.update_app_usage(
            application=app,
            duration_seconds=300 + i * 60  # 5-14 dakika arası
        )
        
        # Dosya aktivitesi
        if i % 3 == 0:
            file_path = f"~/Downloads/{demo_files[i % len(demo_files)]}"
            assistant.activity_logger.log_file_event(
                file_path=file_path,
                event_type="created"
            )
        
        print(f"  📝 Aktivite {i+1}: {app} - {activity}")
    
    print("✅ Demo aktiviteler oluşturuldu!")

def demo_analysis_features(assistant):
    """Analiz özelliklerini demonstre eder"""
    print_header("Analiz Özellikleri Demo")
    
    if not assistant:
        print("❌ Assistant başlatılamadı, analiz atlanıyor.")
        return
    
    print_section("Uygulama Kullanım Analizi")
    app_usage = assistant.analyzer.analyze_app_usage()
    if app_usage:
        for app, duration in app_usage.items():
            print(f"  📱 {app}: {duration}")
    else:
        print("  ℹ️ Henüz uygulama kullanım verisi yok")
    
    print_section("Dosya Aktivite Analizi")
    file_activities = assistant.analyzer.analyze_file_activities(days=1)
    if file_activities:
        print(f"  📁 Aktivite Sayıları: {file_activities.get('activity_counts', 'Veri yok')}")
        print(f"  📄 Dosya Uzantıları: {file_activities.get('top_extensions', 'Veri yok')}")
    else:
        print("  ℹ️ Henüz dosya aktivite verisi yok")
    
    print_section("Otomasyon Önerileri")
    try:
        recommendations = assistant.get_automation_recommendations()
        if recommendations:
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  🔄 {i}. {rec['recommendation']['description']}")
                print(f"     Skor: {rec['score']:.1f}, Öncelik: {rec['priority']}")
        else:
            print("  ℹ️ Henüz otomasyon önerisi yok")
    except Exception as e:
        print(f"  ❌ Otomasyon önerileri alınırken hata: {e}")

def demo_reporting_features(assistant):
    """Rapor özelliklerini demonstre eder"""
    print_header("Raporlama Özellikleri Demo")
    
    if not assistant:
        print("❌ Assistant başlatılamadı, raporlama atlanıyor.")
        return
    
    print_section("Günlük Rapor Oluşturma")
    try:
        report_path = assistant.generate_daily_report()
        if report_path:
            print(f"  ✅ Günlük rapor oluşturuldu: {report_path}")
            
            # Rapor içeriğini göster
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    print(f"  📊 Rapor Tarihi: {report_data.get('date', 'Bilinmiyor')}")
                    print(f"  📱 Uygulama Sayısı: {len(report_data.get('app_usage', {}))}")
        else:
            print("  ❌ Günlük rapor oluşturulamadı")
    except Exception as e:
        print(f"  ❌ Rapor oluşturulurken hata: {e}")
    
    print_section("Veri Export")
    try:
        export_path = assistant.export_data(format="json", days=1)
        if export_path:
            print(f"  ✅ Veriler export edildi: {export_path}")
            
            # Export dosya boyutunu göster
            if os.path.exists(export_path):
                file_size = os.path.getsize(export_path)
                print(f"  📦 Dosya boyutu: {file_size} byte")
        else:
            print("  ❌ Veri export edilemedi")
    except Exception as e:
        print(f"  ❌ Export edilirken hata: {e}")

def demo_interactive_features():
    """İnteraktif özellikler hakkında bilgi verir"""
    print_header("İnteraktif Özellikler")
    
    print("🎛️ Arketic Assistant aşağıdaki interaktif özellikleri sunar:")
    print("\n📋 Ana Komutlar:")
    print("  1. İzlemeyi başlat/durdur")
    print("  2. Günlük/haftalık rapor oluştur")
    print("  3. Aktivite özeti görüntüle")
    print("  4. Otomasyon önerileri al")
    print("  5. Verileri dışa aktar")
    print("  6. Sistem durumu kontrol et")
    
    print("\n🚀 Çalıştırma Modları:")
    print("  • İnteraktif mod: python arketic_assistant.py")
    print("  • Komut satırı: python arketic_assistant.py --start")
    print("  • Rapor oluştur: python arketic_assistant.py --report daily")
    print("  • Export: python arketic_assistant.py --export json")

def demo_cleanup():
    """Demo dosyalarını temizler"""
    print_header("Demo Temizleme")
    
    demo_files = [
        "arketic_demo_config.json",
        "demo_data"
    ]
    
    cleanup_choice = input("\n🗑️ Demo dosyalarını temizlemek istiyor musunuz? (y/n): ").strip().lower()
    
    if cleanup_choice == 'y':
        for item in demo_files:
            try:
                if os.path.isfile(item):
                    os.remove(item)
                    print(f"  ✅ Dosya silindi: {item}")
                elif os.path.isdir(item):
                    import shutil
                    shutil.rmtree(item)
                    print(f"  ✅ Dizin silindi: {item}")
            except Exception as e:
                print(f"  ❌ {item} silinirken hata: {e}")
    else:
        print("  ℹ️ Demo dosyaları korundu")

def main():
    """Ana demo fonksiyonu"""
    print("🚀 Arketic Assistant Demo Script")
    print("Bu script Arketic Assistant'ın temel özelliklerini demonstre eder.")
    
    input("\n⏸️ Devam etmek için Enter tuşuna basın...")
    
    # Demo adımları
    try:
        # 1. Yapılandırma demo
        config_file = demo_configuration()
        input("\n⏸️ Devam etmek için Enter tuşuna basın...")
        
        # 2. Assistant başlatma
        assistant = demo_assistant_initialization(config_file)
        input("\n⏸️ Devam etmek için Enter tuşuna basın...")
        
        # 3. İzleme simülasyonu
        demo_monitoring_simulation(assistant)
        input("\n⏸️ Devam etmek için Enter tuşuna basın...")
        
        # 4. Analiz özellikleri
        demo_analysis_features(assistant)
        input("\n⏸️ Devam etmek için Enter tuşuna basın...")
        
        # 5. Raporlama özellikleri
        demo_reporting_features(assistant)
        input("\n⏸️ Devam etmek için Enter tuşuna basın...")
        
        # 6. İnteraktif özellikler
        demo_interactive_features()
        input("\n⏸️ Devam etmek için Enter tuşuna basın...")
        
        # 7. Temizleme
        demo_cleanup()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Demo sırasında hata: {e}")
    finally:
        print("\n🏁 Demo tamamlandı!")
        print("\n🎯 Arketic Assistant'ı kullanmaya başlamak için:")
        print("   python arketic_assistant.py --interactive")

if __name__ == "__main__":
    main()