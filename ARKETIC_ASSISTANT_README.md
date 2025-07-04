# 🤖 Arketic Assistant - Comprehensive Task Mining Assistant

**Arketic Assistant**, kullanıcıların günlük bilgisayar aktivitelerini izleyen, analiz eden ve otomasyon önerileri sunan gelişmiş bir Task Mining asistanıdır. Bu sistem, orijinal task mining projesinin tüm fonksiyonlarını kapsamlı bir assistant deneyimi altında birleştirir.

## 🎯 Özellikler

### 📊 Comprehensive Monitoring
- **Kullanıcı Aktivite İzleme**: Etkin pencere değişiklikleri, klavye/fare etkileşimleri
- **Tarayıcı Geçmişi İzleme**: Chrome, Firefox, Edge tarayıcı aktiviteleri
- **Dosya Sistemi İzleme**: Çoklu dizin izleme, dosya operasyonları
- **Uygulama Kullanım Analizi**: Detaylı uygulama kullanım süreleri

### 🔍 Advanced Analysis
- **Otomatik Rapor Oluşturma**: Günlük ve haftalık analiz raporları
- **Tekrarlayan Desen Tespiti**: Sık tekrarlanan işlem dizilerinin belirlenmesi
- **Otomasyon Önerileri**: Skorlama sistemi ile öncelikli öneriler
- **Görselleştirme**: Matplotlib ile grafiksel analiz

### 🎛️ Interactive Interface
- **Komut Satırı Arayüzü**: Argparse ile gelişmiş CLI
- **İnteraktif Mod**: Kullanıcı dostu menü sistemi
- **Yapılandırılabilir Ayarlar**: JSON tabanlı konfigürasyon
- **Çoklu Format Desteği**: JSON, CSV, HTML export

## 🛠️ Sistem Gereksinimleri

### Python ve Bağımlılıklar
```bash
Python 3.7+
SQLite3
```

### Gerekli Kütüphaneler
```txt
pygetwindow>=0.0.9
pynput>=1.7.6
watchdog>=2.1.9
browser-history>=0.3.2
psutil>=5.9.0
pywin32>=303
pandas>=1.4.2
matplotlib>=3.5.2
Pillow>=9.0.0
```

## 🚀 Kurulum ve Başlangıç

### 1. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 2. Arketic Assistant'ı Başlat
```bash
# İnteraktif mod (varsayılan)
python arketic_assistant.py

# Belirli komutlar
python arketic_assistant.py --start          # İzlemeyi başlat
python arketic_assistant.py --interactive    # İnteraktif mod
python arketic_assistant.py --report daily   # Günlük rapor
python arketic_assistant.py --report weekly  # Haftalık rapor
python arketic_assistant.py --export json    # Veri dışa aktarma
```

## 📋 Kullanım Modları

### 1. İnteraktif Mod
```
🤖 Arketic Assistant - İnteraktif Mod
==================================================

📋 Mevcut Komutlar:
1. İzlemeyi başlat
2. İzlemeyi durdur
3. Günlük rapor oluştur
4. Haftalık rapor oluştur
5. Aktivite özeti göster
6. Otomasyon önerileri göster
7. Verileri dışa aktar
8. Durumu kontrol et
9. Çıkış
```

### 2. Komut Satırı Modu
```bash
# Yapılandırma dosyası ile çalıştır
python arketic_assistant.py --config my_config.json

# Belirli gün sayısı ile analiz
python arketic_assistant.py --export json --days 14

# Arka planda çalıştır
python arketic_assistant.py --start &
```

## ⚙️ Yapılandırma

### arketic_config.json
```json
{
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
    "daily_auto_generate": true,
    "weekly_auto_generate": true
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
    "mask_sensitive_data": true,
    "data_retention_days": 30
  }
}
```

## 📊 Veri Analizi ve Raporlama

### Analiz Türleri
1. **Uygulama Kullanım Analizi**
   - Günlük/haftalık kullanım süreleri
   - Trend analizi
   - Zaman dağılımı

2. **Tarayıcı Deseni Analizi**
   - En çok ziyaret edilen siteler
   - Günlük ortalama ziyaret sayısı
   - Domain bazlı istatistikler

3. **Dosya Aktivite Analizi**
   - Dosya tipi dağılımı
   - Saatlik aktivite analizi
   - İndirme desenleri

4. **Tekrarlayan Desen Tespiti**
   - Sık tekrarlanan uygulama dizileri
   - Otomasyon adayları
   - Süre bazlı öncelik skoru

### Otomatik Rapor Oluşturma
```python
# Günlük rapor
assistant.generate_daily_report()

# Haftalık rapor
assistant.generate_weekly_report()

# Özelleştirilebilir analiz
summary = assistant.get_activity_summary(days=14)
recommendations = assistant.get_automation_recommendations()
```

## 🔄 Otomasyon Önerileri

### Skorlama Sistemi
- **Yüksek Öncelik (50+ puan)**: Kritik otomasyon adayları
- **Orta Öncelik (20-49 puan)**: Değerlendirilmesi gereken adaylar
- **Düşük Öncelik (<20 puan)**: Uzun vadeli otomasyon adayları

### Otomasyon Türleri
1. **Sequence-Based**: Tekrarlayan uygulama dizileri
2. **Duration-Based**: Uzun süreli uygulama kullanımları
3. **Activity-Based**: Yoğun dosya operasyonları

## 📁 Proje Yapısı

```
arketic-assistant/
├── arketic_assistant.py          # Ana assistant sınıfı
├── arketic_config.json           # Yapılandırma dosyası
├── activity_logger.py            # Veritabanı işlemleri
├── analyzer.py                   # Analiz ve raporlama
├── event_listener.py             # Olay izleme
├── file_watcher.py               # Dosya sistemi izleme
├── browser_log.py                # Tarayıcı geçmişi
├── requirements.txt              # Bağımlılıklar
├── utils/
│   └── time_utils.py             # Zaman yardımcı fonksiyonları
└── data/
    ├── arketic_activity.db       # Ana veritabanı
    ├── arketic.log               # Sistem logları
    └── reports/                  # Oluşturulan raporlar
        ├── daily_report_*.json
        ├── weekly_report_*.json
        └── arketic_export_*.json
```

## 🔍 Veritabanı Şeması

### Tablolar
- **user_events**: Kullanıcı aktiviteleri ve pencere değişiklikleri
- **file_events**: Dosya sistemi olayları
- **browser_events**: Tarayıcı geçmişi kayıtları
- **app_usage**: Uygulama kullanım süreleri

### Örnek Sorgular
```sql
-- En çok kullanılan uygulamalar
SELECT application, SUM(duration_seconds) as total_time
FROM app_usage
GROUP BY application
ORDER BY total_time DESC;

-- Günlük tarayıcı aktivitesi
SELECT DATE(timestamp) as date, COUNT(*) as visits
FROM browser_events
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## 🛡️ Güvenlik ve Gizlilik

### Veri Güvenliği
- **Yerel Veri Saklama**: Tüm veriler yerel makinede saklanır
- **Şifreleme**: Hassas verilerin maskelenmesi
- **Veri Saklama Süresi**: Yapılandırılabilir saklama politikası

### Gizlilik Ayarları
```json
"privacy": {
  "mask_sensitive_data": true,
  "data_retention_days": 30,
  "exclude_apps": ["password_manager", "banking_app"]
}
```

## 📈 Performans İyileştirmeleri

### SQLite Optimizasyonları
- **WAL Modu**: Write-Ahead Logging
- **Batch İşlemler**: Toplu veri yazma
- **İndeksleme**: Hızlı sorgu performansı

### Çoklu Thread Yapısı
- **Ayrı İzleme Thread'leri**: Paralel izleme
- **Asenkron Rapor Oluşturma**: Kesintisiz izleme
- **Kaynak Optimizasyonu**: Düşük sistem etkisi

## 🧪 Test ve Geliştirme

### Test Senaryoları
```bash
# Temel işlevsellik testi
python arketic_assistant.py --interactive

# Rapor oluşturma testi
python arketic_assistant.py --report daily

# Veri export testi
python arketic_assistant.py --export json --days 1
```

### Geliştirme Modları
```bash
# Debug modu
python arketic_assistant.py --config debug_config.json

# Verbose logging
python arketic_assistant.py --start --verbose
```

## 🔧 Sorun Giderme

### Yaygın Sorunlar
1. **Veritabanı Bağlantı Hatası**
   - `data/` dizininin yazma izinlerini kontrol edin
   - SQLite versiyonunu kontrol edin

2. **Tarayıcı Geçmişi Alınamıyor**
   - Tarayıcı kapatılmış olduğundan emin olun
   - Tarayıcı profillerini kontrol edin

3. **İzleme Başlamıyor**
   - Sistem yetkilendirmelerini kontrol edin
   - Antivirus yazılımı engellemelerini kontrol edin

### Log Dosyaları
```bash
# Ana log dosyası
tail -f data/arketic.log

# Hata analizi
grep ERROR data/arketic.log
```

## 📚 API Referansı

### Ana Sınıf
```python
class ArketicAssistant:
    def __init__(self, config_file: str = "arketic_config.json")
    def start_monitoring(self)
    def stop_monitoring(self)
    def generate_daily_report(self) -> Optional[str]
    def generate_weekly_report(self) -> Optional[str]
    def get_activity_summary(self, days: int = 1) -> Dict
    def get_automation_recommendations(self) -> List[Dict]
    def export_data(self, format: str = "json", days: int = 7) -> Optional[str]
    def interactive_mode(self)
```

### Kullanım Örneği
```python
from arketic_assistant import ArketicAssistant

# Assistant'ı başlat
assistant = ArketicAssistant("my_config.json")

# İzlemeyi başlat
assistant.start_monitoring()

# Analiz yap
summary = assistant.get_activity_summary(days=7)
recommendations = assistant.get_automation_recommendations()

# Rapor oluştur
report_path = assistant.generate_daily_report()
```

## 🤝 Katkıda Bulunma

### Geliştirme Ortamı
```bash
# Proje klonu
git clone <repository-url>
cd arketic-assistant

# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### Kod Standartları
- **PEP 8**: Python kod standartları
- **Type Hints**: Tür belirteçleri kullanın
- **Docstring**: Fonksiyon dokümantasyonu
- **Logging**: Uygun log seviyelerini kullanın

## 📄 Lisans

Bu proje, orijinal task mining projesinin tüm fonksiyonlarını içeren kapsamlı bir assistant implementasyonudur. Tüm kod ve dokümantasyon MIT lisansı altında sunulmaktadır.

---

**🚀 Arketic Assistant ile task mining deneyiminizi bir üst seviyeye taşıyın!**

Bu comprehensive assistant, orijinal task mining projesinin tüm bilgi ve fonksiyonlarını tek bir güçlü platform altında birleştirir ve kullanıcıların günlük aktivitelerini izleyerek otomasyon fırsatlarını tespit etmelerine yardımcı olur.