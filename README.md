# Task Mining Prototipi

Bu proje, kullanıcıların günlük bilgisayar aktivitelerini izleyen, kaydeden ve analiz eden bir Task Mining uygulamasıdır. Uygulama, manuel işlemlerin tespiti ve potansiyel otomasyon fırsatlarının belirlenmesi amacıyla aktivite verilerini izler ve analiz eder.

## 📋 Özellikler

- **Kullanıcı Aktivite İzleme**
  - Etkin pencere değişiklikleri
  - Klavye ve fare etkileşimleri
  - Uygulama kullanım süreleri

- **Chrome Tarayıcı Geçmişi İzleme**
  - Ziyaret edilen sayfalar
  - Ziyaret süreleri ve sıklıkları

- **Dosya Sistemi İzleme**
  - Yeni dosya oluşturma
  - Dosya silme ve değiştirme
  - İndirilen dosyaları takip etme

- **Veri Analizi ve Raporlama**
  - Günlük ve haftalık analiz raporları
  - Uygulama kullanım istatistikleri
  - Tekrarlanan işlem dizilerinin tespiti
  - Grafiksel görselleştirmeler

## 🛠️ Teknolojiler ve Kütüphaneler

- **Python 3.7+**
- **SQLite3**: Veritabanı yönetimi
- **Pandas**: Veri analizi
- **Matplotlib**: Veri görselleştirme
- **PyGetWindow**: Pencere değişikliklerini izleme
- **Pynput**: Klavye ve fare olaylarını izleme
- **Watchdog**: Dosya sistemi değişikliklerini izleme

## 📁 Proje Yapısı

```
task-mining/
├── main.py                   # Ana başlatma scripti
├── activity_logger.py        # Veritabanı işlemleri
├── event_listener.py         # Klavye/fare ve pencere izleme
├── file_watcher.py           # Dosya sistemi izleme
├── browser_log.py            # Chrome tarayıcı geçmişi izleme
├── analyzer.py               # Veri analizi ve raporlama
├── requirements.txt          # Bağımlılıklar
├── utils/                    # Yardımcı modüller
│   └── time_utils.py         # Zaman işlemleri için yardımcı fonksiyonlar
├── data/                     # Veri dizini
│   ├── activity.db           # SQLite veritabanı
│   └── reports/              # Oluşturulan raporlar ve grafikler
└── temp/                     # Geçici dosyalar
```

## 📊 Veritabanı Şeması

### user_events
- `timestamp`: ISO 8601 formatında zaman damgası
- `window_title`: Aktif pencere başlığı
- `application`: Uygulama adı
- `event_type`: Olay türü (klavye, fare_tıklama, pencere_değişimi)
- `event_details`: Olay detayları

### file_events
- `timestamp`: ISO 8601 formatında zaman damgası
- `file_path`: Etkilenen dosya yolu
- `event_type`: Olay türü (oluşturuldu, silindi, değiştirildi, taşındı)

### browser_events
- `timestamp`: ISO 8601 formatında zaman damgası
- `url`: Ziyaret edilen URL
- `title`: Sayfa başlığı
- `browser`: Tarayıcı adı (şu anda sadece Chrome)

### app_usage
- `date`: Tarih (YYYY-MM-DD)
- `application`: Uygulama adı
- `duration_seconds`: O gün için toplam kullanım süresi (saniye)

## 🚀 Kurulum ve Kullanım

### Bağımlılıkların Yüklenmesi

```bash
pip install -r requirements.txt
```

### Uygulamayı Çalıştırma

```bash
python main.py
```

Uygulama, aktiviteleri izlemeye başlayacak ve belirlenen aralıklarla raporlar oluşturacaktır. Raporlar `data/reports` dizininde saklanır.

## 🧩 Bileşen Açıklamaları

### main.py
Ana kontrol scripti, tüm bileşenleri başlatır ve koordine eder. Kullanıcı aktiviteleri, dosya değişiklikleri ve tarayıcı geçmişini izlemek için ayrı thread'ler oluşturur.

### activity_logger.py
Veritabanı işlemlerini yönetir. SQLite'ın Write-Ahead Logging (WAL) modunu kullanarak verimli veritabanı yazma işlemleri sağlar. Tüm aktivite kayıtları, bu bileşen aracılığıyla veritabanına kaydedilir.

### event_listener.py
PyGetWindow ve Pynput kütüphanelerini kullanarak kullanıcının pencere değişikliklerini, klavye ve fare aktivitelerini izler.

### file_watcher.py
Watchdog kütüphanesini kullanarak dosya sistemi değişikliklerini izler. Varsayılan olarak kullanıcının İndirilenler klasörünü izler.

### browser_log.py
Chrome tarayıcısının geçmiş veritabanını 10 saniye aralıklarla kontrol eder. Chrome'un geçmiş veritabanı kilitli olabileceğinden, bir kopyasını alır ve bu kopyadan okuma yapar.

### analyzer.py
Toplanan verileri analiz eder ve raporlar oluşturur. Uygulama kullanım süreleri, sık tekrarlanan aktivite dizileri, tarayıcı kullanım desenleri ve dosya aktivitelerini analiz eder. Matplotlib kullanarak grafiksel görselleştirmeler oluşturur.

### utils/time_utils.py
Zaman ile ilgili yardımcı fonksiyonlar sağlar. Zaman damgaları oluşturma, süre formatlamaları ve zaman dilimi dönüşümleri gibi işlemleri içerir.

## 📈 Raporlar

Uygulama iki tür rapor oluşturur:

### Günlük Raporlar
- Her tarayıcı aktivitesi değişikliğinde otomatik olarak güncellenir
- Günlük uygulama kullanım süreleri
- Tarayıcı aktiviteleri
- Dosya işlemleri
- Potansiyel otomasyon adayları

### Haftalık Raporlar
- Her dakika otomatik olarak güncellenir
- Son 7 günün uygulama kullanım trendleri
- Tarayıcı kullanım desenleri
- Dosya aktivite istatistikleri
- Sık tekrarlanan aktivite dizileri

## 📊 Görselleştirmeler

Uygulama, raporlarla birlikte şu görselleştirmeleri oluşturur:

- **Uygulama Kullanım Süreleri**: Bar grafiği
- **Dosya Aktiviteleri Dağılımı**: Pasta grafiği
- **Tarayıcı Alan Adları**: Yatay bar grafiği

## ⚙️ Gelişmiş Özellikler

- **Gerçek Zamanlı İzleme**: Aktiviteler anında tespit edilir ve kaydedilir
- **Veritabanı Optimizasyonu**: SQLite WAL modu ile daha hızlı ve güvenli veritabanı işlemleri
- **Chrome Entegrasyonu**: Chrome tarayıcısının geçmiş veritabanı ile doğrudan entegrasyon
- **Otonom Chrome Yönetimi**: Chrome'un çalışmadığı durumlarda otomatik başlatma

## 🔄 Geliştirme Akışı

1. **Ana Thread**: main.py tarafından yönetilir, tüm bileşenleri koordine eder
2. **Aktivite İzleme Thread'leri**: Klavye/fare olayları, pencere değişiklikleri ve dosya sistemi değişikliklerini izler
3. **Tarayıcı İzleme Thread'i**: Chrome geçmiş veritabanını 10 saniyede bir kontrol eder
4. **Analiz ve Raporlama**: Tarayıcı aktivitelerinde değişiklik olduğunda ve her dakika gerçekleştirilir

## 🛡️ Gizlilik ve Güvenlik

- Tüm veriler yerel olarak saklanır, hiçbir veri dışarı gönderilmezz
- Klavye girdisi kaydedilirken alfanümerik olmayan karakterler maskelenir
- Veritabanı yalnızca uygulamanın kendi kullanımı içindir

## 🧪 Test

Uygulamayı test etmek için:

1. Uygulamayı başlatın: `python main.py`
2. Chrome tarayıcısında birkaç web sitesi ziyaret edin
3. Belgeleri düzenleyin veya İndirilenler klasörüne dosyalar ekleyin
4. Farklı uygulamaları kullanın
5. `data/reports` dizinindeki raporları kontrol edin

## 🔍 Sorun Giderme

- **Chrome Geçmişi Alınamıyor**: Chrome'un çalışır durumda olduğundan emin olun
- **Veritabanı Güncellenmiyor**: temp dizininin yazma izinlerine sahip olduğunu kontrol edin
- **Raporlar Oluşturulmuyor**: data/reports dizininin mevcut olduğunu kontrol edin 