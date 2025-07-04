# Jira Windows Automation - Kullanım Kılavuzu

**Tarih:** 2025-07-04  
**Yazar:** user  
**Sistem:** Windows Chrome Otomasyonu ile Jira Entegrasyonu

---

## 🎯 Genel Bakış

Bu sistem, Windows ortamında Chrome tarayıcısı üzerinden Jira'ya otomatik bağlantı kurar ve PM Assistant ile entegre çalışarak proje yönetimi task'larını otomatikleştirir.

### Ana Özellikler

- **🔐 Güvenli Şifre Yönetimi**: İlk girişte şifre sorar, sonraki girişlerde otomatik giriş
- **🌐 Chrome Otomasyonu**: Windows'ta Chrome'u otomatik açar ve kontrol eder
- **📋 Task Yönetimi**: Jira'da Epic, Story, Task oluşturma ve yönetme
- **🔄 PM Assistant Entegrasyonu**: Fikirlerden otomatik Jira task'ları
- **📊 Raporlama**: Task durumu ve senkronizasyon raporları

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
# Kurulum scriptini çalıştır
cd jira_automation
python setup_jira_automation.py

# Veya tüm testlerle birlikte
python setup_jira_automation.py --test-all
```

### 2. Konfigürasyon

`jira_config_template.json` dosyasını düzenleyin:

```json
{
  "jira_url": "https://yourcompany.atlassian.net",
  "username": "your-email@domain.com",
  "default_project_key": "PROJ"
}
```

### 3. İlk Çalıştırma

```bash
# Ana entegrasyon sistemini başlat
python pm_jira_integration.py

# Veya sadece Jira otomasyonu
python jira_windows_automation.py
```

---

## 📖 Kullanım Senaryoları

### Senaryo 1: Proje Fikirlerinden Jira Task'ları

```
1. PM-Jira Integration'ı başlatın
2. "Proje fikirlerini analiz et" seçeneğini seçin
3. Fikirlerinizi yazın:
   "Bir mobil uygulama geliştirmek istiyoruz.
    Kritik özellikler: kullanıcı girişi, push notification.
    Güvenlik önemli, 3 ay içinde tamamlanmalı."
4. Sistem otomatik olarak:
   - Fikirleri PMI kategorilerine ayırır
   - Jira'da Epic/Story/Task oluşturur
   - PM Assistant'ta kaydeder
```

### Senaryo 2: Mevcut Jira Task'larını İçe Aktarma

```
1. "Jira task'larını senkronize et" seçeneğini seçin
2. Sistem mevcut Jira task'larınızı bulur
3. PM Assistant'a import eder
4. İki taraflı senkronizasyon sağlar
```

### Senaryo 3: Jira'da Manuel Task Oluşturma

```
1. Jira otomasyonunu başlatın
2. "Yeni görev oluştur" seçeneğini seçin
3. Proje, başlık, açıklama girin
4. Sistem otomatik olarak Jira'da task oluşturur
```

---

## 🔧 Sistem Bileşenleri

### Ana Modüller

| Modül | Açıklama | Sorumluluklar |
|-------|----------|---------------|
| **jira_windows_automation.py** | Temel Jira otomasyonu | Chrome kontrolü, login, task CRUD |
| **pm_jira_integration.py** | PM Assistant entegrasyonu | İki taraflı senkronizasyon, analiz |
| **setup_jira_automation.py** | Kurulum ve test | Bağımlılık kurulumu, sistem testi |

### Veri Akışı

```
Kullanıcı Girişi
       ↓
PM Assistant Analizi (PMI kategorileri)
       ↓
Jira Task Oluşturma (Epic/Story/Task)
       ↓
Task Mapping Kaydı
       ↓
Senkronizasyon ve Raporlama
```

---

## ⚙️ Detaylı Konfigürasyon

### Şifre Yönetimi

Sistem 3 seviyeli şifre yönetimi kullanır:

1. **Keyring (Önerilen)**: Windows Credential Manager'da güvenli depolama
2. **Oturum Belleği**: Sadece program çalışırken hafızada
3. **Manual**: Her seferinde şifre sorma

```python
# Şifre yönetimi ayarları
KEYRING_AVAILABLE = True  # Otomatik detect
save_password = input("Şifrenizi kaydetmek istiyor musunuz? (y/n): ")
```

### PMI-Jira Mapping

PMI kategorilerinin Jira Issue Type'larına dönüşümü:

```json
{
  "category_mapping": {
    "vision": "Epic",      // Üst seviye hedefler
    "scope": "Epic",       // Proje kapsamı 
    "deliverable": "Story", // Somut çıktılar
    "milestone": "Story",   // Zaman hedefleri
    "risk": "Task",        // Risk yönetimi
    "dependency": "Task"   // Bağımlılıklar
  }
}
```

### Chrome Ayarları

Sistem otomatik olarak Chrome'u bulur ve ayarlar:

```python
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--user-data-dir=jira_automation_profile")
```

---

## 🛠️ Gelişmiş Özellikler

### Task Mapping Sistemi

Her PM Assistant fikri ile Jira task'ı arasında mapping kaydedilir:

```json
{
  "pm_idea_id": {
    "jira_key": "PROJ-123",
    "category": "vision", 
    "created_at": "2025-07-04T10:30:00",
    "status": "In Progress",
    "source": "pm_analysis"
  }
}
```

### Otomatik Senkronizasyon

```python
# Otomatik senkronizasyon ayarları
config = {
  "auto_sync": True,
  "sync_interval_minutes": 30,
  "bidirectional_sync": True
}
```

### Raporlama Sistemi

3 tip rapor oluşturulur:

1. **Task Status Report**: Mevcut durumun özeti
2. **PM Assistant Report**: PMI metodolojisi raporları
3. **Sync Report**: Senkronizasyon istatistikleri

---

## 🔍 Sorun Giderme

### Yaygın Sorunlar ve Çözümler

#### 1. Chrome Bulunamadı

```
Hata: Chrome WebDriver başlatma hatası
Çözüm: 
- Chrome'un kurulu olduğundan emin olun
- ChromeDriver'ı manuel kurun: chromedriver.chromium.org
```

#### 2. Jira Giriş Başarısız

```
Hata: Giriş sayfası elementleri bulunamadı
Çözüm:
- Jira URL'inin doğru olduğunu kontrol edin
- Kullanıcı adı/şifrenizi kontrol edin
- 2FA aktifse app password kullanın
```

#### 3. Task Oluşturulamadı

```
Hata: Project seçimi hatası
Çözüm:
- Proje anahtarının doğru olduğunu kontrol edin
- Jira'da proje oluşturma yetkisine sahip olduğunuzu kontrol edin
```

#### 4. PM Assistant Import Hatası

```
Hata: PM Assistant modülleri bulunamadı
Çözüm:
- Python path'inin doğru ayarlandığından emin olun
- PM Assistant'ın kurulu olduğunu kontrol edin
```

### Debug Modu

```python
# Logging seviyesini debug'a alın
logging.basicConfig(level=logging.DEBUG)

# Chrome'u görünür modda çalıştırın
chrome_options.add_argument("--disable-headless")
```

### Log Dosyaları

```
jira_automation.log          # Jira otomasyonu logları
pm_jira_integration.log      # Entegrasyon logları
data/pm_assistant.log        # PM Assistant logları
```

---

## 📊 Performans ve Güvenlik

### Performans Optimizasyonu

```python
# Chrome bellek kullanımını optimize edin
chrome_options.add_argument("--memory-pressure-off")
chrome_options.add_argument("--disable-dev-shm-usage")

# Task mapping veritabanını temizleyin
cleanup_old_mappings(days_old=90)
```

### Güvenlik Önlemleri

1. **Şifre Şifreleme**: Keyring kullanarak şifreler şifrelenir
2. **Session Yönetimi**: Chrome profili izole edilir
3. **API Token**: Jira API token kullanımı önerilir
4. **Audit Trail**: Tüm işlemler loglanır

---

## 🔄 API Referansı

### JiraWindowsAutomation Sınıfı

```python
class JiraWindowsAutomation:
    def login_to_jira() -> bool:
        """Jira'ya giriş yapar"""
        
    def create_task(project_key, summary, description, issue_type) -> str:
        """Yeni task oluşturur, Jira key döndürür"""
        
    def get_my_tasks() -> List[Dict]:
        """Kullanıcının task'larını listeler"""
        
    def open_task(task_key) -> bool:
        """Belirli bir task'ı açar"""
```

### PMJiraIntegration Sınıfı

```python
class PMJiraIntegration:
    def analyze_and_create_tasks(user_input, project_key) -> Dict:
        """Kullanıcı girişini analiz eder ve Jira task'ları oluşturur"""
        
    def sync_jira_tasks_to_pm() -> List[Dict]:
        """Jira task'larını PM Assistant'a senkronize eder"""
        
    def get_task_status_report() -> Dict:
        """Task durumu raporu oluşturur"""
```

---

## 🚀 İleri Düzey Kullanım

### Batch Task Oluşturma

```python
# Çoklu task oluşturma
ideas = [
    {"summary": "User Authentication", "category": "deliverable"},
    {"summary": "Payment Security", "category": "risk"},
    {"summary": "Q1 Release", "category": "milestone"}
]

for idea in ideas:
    jira_key = automation.create_task(
        project_key="PROJ",
        summary=idea["summary"],
        description=f"Category: {idea['category']}",
        issue_type=category_mapping[idea["category"]]
    )
```

### Custom PMI Categories

```python
# Kendi PMI kategorilerinizi ekleyin
custom_categories = {
    "technical_debt": "Task",
    "user_research": "Story", 
    "compliance": "Epic"
}

config["category_mapping"].update(custom_categories)
```

### Webhook Entegrasyonu

```python
# Jira webhook'larını dinleyerek otomatik senkronizasyon
def handle_jira_webhook(data):
    if data["issue_event_type_name"] == "issue_updated":
        sync_single_task(data["issue"]["key"])
```

---

## 📈 Başarı Metrikleri

### Kullanım İstatistikleri

Sistem aşağıdaki metrikleri takip eder:

- **Task Oluşturma Hızı**: Manuel vs Otomatik
- **Senkronizasyon Başarı Oranı**: %95+ hedeflenir
- **Kullanıcı Memnuniyeti**: Zaman tasarrufu ölçümü
- **Hata Oranları**: Log bazlı hata analizi

### ROI Hesaplama

```
Manuel Task Oluşturma: 5 dakika/task
Otomatik Task Oluşturma: 30 saniye/task
Zaman Tasarrufu: %90

Aylık 100 task için:
Manuel: 500 dakika (8.3 saat)
Otomatik: 50 dakita (0.8 saat)
Tasarruf: 7.5 saat/ay
```

---

## 🤝 Topluluk ve Destek

### Katkıda Bulunma

1. Fork yapın ve branch oluşturun
2. Özelliğinizi geliştirin
3. Test edin ve belgeleyin
4. Pull request açın

### Destek Kanalları

- **GitHub Issues**: Bug raporları ve özellik istekleri
- **Documentation**: Bu kılavuz ve kod içi belgeler
- **Logs**: Detaylı hata analizi için log dosyaları

### Versiyon Geçmişi

- **v1.0.0**: İlk kararlı sürüm
- **v1.1.0**: PM Assistant entegrasyonu
- **v1.2.0**: Batch operations (gelecek)

---

## 📋 Ek Kaynaklar

### Faydalı Linkler

- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Selenium Python Documentation](https://selenium-python.readthedocs.io/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)

### Şablon Dosyalar

- `jira_config_template.json`: Temel konfigürasyon
- `start_jira_automation.bat`: Windows başlatma scripti
- `task_mapping_template.json`: Task mapping şablonu

### Test Veri Setleri

```json
{
  "test_scenarios": [
    {
      "name": "E-commerce Project",
      "input": "Bir e-ticaret platformu geliştirmek istiyoruz...",
      "expected_tasks": 5,
      "categories": ["vision", "scope", "deliverable"]
    }
  ]
}
```

---

**Son Güncelleme:** 2025-07-04  
**Doküman Versiyonu:** 1.0  
**Sistem Gereksinimleri:** Windows 10+, Python 3.7+, Chrome 90+