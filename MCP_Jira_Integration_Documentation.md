# MCP Jira Integration Documentation
## Model Context Protocol ile Jira Entegrasyonu - Cursor İçin Kapsamlı Rehber

### 📋 İçindekiler

1. [MCP Nedir?](#mcp-nedir)
2. [Jira MCP Server Yetenekleri](#jira-mcp-server-yetenekleri)
3. [Kurulum ve Konfigürasyon](#kurulum-ve-konfigürasyon)
4. [Jira MCP Server Türleri](#jira-mcp-server-türleri)
5. [Araçlar ve Fonksiyonlar](#araçlar-ve-fonksiyonlar)
6. [Güvenlik ve Kimlik Doğrulama](#güvenlik-ve-kimlik-doğrulama)
7. [Cursor ile Entegrasyon](#cursor-ile-entegrasyon)
8. [Kullanım Senaryoları](#kullanım-senaryoları)
9. [Analiz ve Raporlama](#analiz-ve-raporlama)
10. [Troubleshooting](#troubleshooting)
11. [Örnek Komutlar](#örnek-komutlar)

---

## MCP Nedir?

Model Context Protocol (MCP), büyük dil modelleri (LLM) ile harici veri kaynaklarını ve araçları standartlaştırılmış bir şekilde birbirine bağlayan açık kaynaklı bir protokoldür. MCP, yapay zeka sistemlerinin harici sistemlerle güvenli ve kontrollü şekilde etkileşim kurmasını sağlar.

### MCP'nin Temel Bileşenleri

#### 1. **Tools (Araçlar)**
- Yürütülebilir fonksiyonlar
- API çağrıları yapma
- Veritabanı sorgulama
- Dosya operasyonları

#### 2. **Resources (Kaynaklar)**
- Yapılandırılmış veri akışları
- Dosyalar ve API yanıtları
- Gerçek zamanlı veri kaynakları

#### 3. **Prompts (Komutlar)**
- Yeniden kullanılabilir komut şablonları
- Tutarlı etkileşim sağlama
- Önceden tanımlanmış iş akışları

### MCP Mimarisi

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │    │    MCP Server    │    │  External API   │
│   (Cursor)      │◄──►│   (Jira MCP)     │◄──►│     (Jira)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## Jira MCP Server Yetenekleri

### 🎯 Temel Özellikler

#### **Issue Yönetimi**
- ✅ Issue arama (JQL desteği)
- ✅ Issue detaylarını görüntüleme
- ✅ Yeni issue oluşturma
- ✅ Issue güncelleme
- ✅ Issue durumu değiştirme
- ✅ Issue'ya yorum ekleme
- ✅ Issue'ya dosya ekleme

#### **Proje Yönetimi**
- ✅ Proje listesi alma
- ✅ Proje detaylarını görüntüleme
- ✅ Proje üyelerini listeleme
- ✅ Proje konfigürasyonu görüntüleme

#### **Sprint ve Workflow Yönetimi**
- ✅ Sprint listeleme
- ✅ Sprint detaylarını görüntüleme
- ✅ Board listeleme
- ✅ Workflow durumlarını görüntüleme

#### **Gelişmiş Özellikler**
- ✅ Epic ve alt görevler
- ✅ İlişkili issue'lar
- ✅ Attachments yönetimi
- ✅ Kullanıcı ve izin yönetimi
- ✅ Gerçek zamanlı veri senkronizasyonu

### 🔧 Desteklenen Jira Türleri

1. **Jira Cloud** (Atlassian hosted)
2. **Jira Server/Data Center** (Self-hosted)

---

## Kurulum ve Konfigürasyon

### Cursor için MCP Konfigürasyonu

#### 1. Claude Desktop Konfigürasyonu
```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@cosmix/jira-mcp"],
      "env": {
        "JIRA_API_TOKEN": "your-api-token",
        "JIRA_BASE_URL": "https://your-domain.atlassian.net",
        "JIRA_USER_EMAIL": "your-email@company.com",
        "JIRA_TYPE": "cloud"
      }
    }
  }
}
```

#### 2. VS Code Konfigürasyonu
```json
{
  "mcp": {
    "servers": {
      "jira": {
        "command": "npx",
        "args": ["-y", "@cosmix/jira-mcp"],
        "env": {
          "JIRA_API_TOKEN": "your-api-token",
          "JIRA_BASE_URL": "https://your-domain.atlassian.net",
          "JIRA_USER_EMAIL": "your-email@company.com"
        }
      }
    }
  }
}
```

#### 3. Docker Konfigürasyonu
```json
{
  "mcpServers": {
    "jira": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--env-file", "/path/to/.env",
        "ghcr.io/cosmix/jira-mcp:latest"
      ]
    }
  }
}
```

### Environment Variables

```bash
# .env dosyası
JIRA_API_TOKEN=your_api_token_here
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_USER_EMAIL=your-email@company.com
JIRA_TYPE=cloud  # veya 'server' for self-hosted
JIRA_SSL_VERIFY=true
MCP_VERBOSE=true
```

---

## Jira MCP Server Türleri

### 1. **@cosmix/jira-mcp** (Önerilen)
- **Özellikler**: Tam featured, optimized payloads
- **Dil**: TypeScript
- **Maksimum**: 50 search results, 100 epic children
- **Ekstra**: Relationship tracking, data cleaning

### 2. **@CamdenClark/jira-mcp**
- **Özellikler**: Basit ve kullanıcı dostu
- **Dil**: JavaScript
- **Araçlar**: JQL search, issue details

### 3. **@samuelrizzo/jira-mcp-server**
- **Özellikler**: Proje yönetimi odaklı
- **Dil**: TypeScript
- **Araçlar**: Sprint management, member management

### 4. **Python-based Servers**
- **Özellikler**: Python geliştirici dostu
- **Dil**: Python
- **Araçlar**: Custom implementations

---

## Araçlar ve Fonksiyonlar

### 🔍 Search ve Query Araçları

#### `search_issues`
```javascript
{
  "searchString": "project = 'PROJ' AND status = 'Open'",
  "maxResults": 50
}
```

#### `jql_search`
```javascript
{
  "jql": "project = 'PROJ' AND assignee = currentUser()",
  "fields": ["summary", "status", "assignee"],
  "maxResults": 25
}
```

### 📝 Issue Yönetimi Araçları

#### `create_issue`
```javascript
{
  "projectKey": "PROJ",
  "issueType": "Task",
  "summary": "Yeni görev",
  "description": "Detaylı açıklama",
  "assigneeName": "john.doe",
  "fields": {
    "priority": "High",
    "labels": ["backend", "urgent"]
  }
}
```

#### `update_issue`
```javascript
{
  "issueKey": "PROJ-123",
  "fields": {
    "summary": "Güncellenmiş başlık",
    "description": "Güncellenmiş açıklama",
    "assignee": "jane.doe"
  }
}
```

#### `get_issue`
```javascript
{
  "issueId": "PROJ-123",
  "expand": "comments,attachments,subtasks"
}
```

### 💬 Yorum ve Dosya Araçları

#### `add_comment`
```javascript
{
  "issueIdOrKey": "PROJ-123",
  "body": "Bu issue ile ilgili güncellemeler..."
}
```

#### `add_attachment`
```javascript
{
  "issueKey": "PROJ-123",
  "filename": "screenshot.png",
  "fileContent": "base64_encoded_content"
}
```

### 📊 Proje ve Sprint Araçları

#### `list_projects`
```javascript
{
  "jiraHost": "your-domain.atlassian.net",
  "email": "your-email@company.com",
  "apiToken": "your-api-token"
}
```

#### `list_sprints`
```javascript
{
  "boardId": 123,
  "state": "active",
  "projectKey": "PROJ"
}
```

### 👥 Kullanıcı ve Üye Araçları

#### `list_project_members`
```javascript
{
  "projectKey": "PROJ"
}
```

#### `check_user_issues`
```javascript
{
  "projectKey": "PROJ",
  "userName": "john.doe"
}
```

---

## Güvenlik ve Kimlik Doğrulama

### API Token Oluşturma

1. **Atlassian hesabınıza gidin**: https://id.atlassian.com
2. **Security** bölümüne gidin
3. **API tokens** altında **Create API token** seçin
4. Token'a açıklayıcı bir isim verin
5. Token'ı güvenli bir yerde saklayın

### Güvenlik En İyi Uygulamaları

```bash
# Environment variables kullanın
export JIRA_API_TOKEN="your-secure-token"
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_USER_EMAIL="your-email@company.com"

# .env dosyasını .gitignore'a ekleyin
echo ".env" >> .gitignore
```

### İzinler ve Erişim Kontrolleri

- **Project permissions**: Proje bazında erişim
- **Issue permissions**: Issue türü bazında erişim
- **Field permissions**: Alan bazında erişim
- **Workflow permissions**: Durum geçişi bazında erişim

---

## Cursor ile Entegrasyon

### Cursor'da MCP Kullanımı

#### 1. MCP Server Kurulumu
```bash
# Cursor settings.json
{
  "mcp.servers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@cosmix/jira-mcp"],
      "env": {
        "JIRA_API_TOKEN": "${env:JIRA_API_TOKEN}",
        "JIRA_BASE_URL": "${env:JIRA_BASE_URL}",
        "JIRA_USER_EMAIL": "${env:JIRA_USER_EMAIL}"
      }
    }
  }
}
```

#### 2. Cursor ile Jira Komutları

**Issue Arama:**
```
@jira PROJ projesinde açık olan tüm task'ları listele
```

**Issue Oluşturma:**
```
@jira PROJ projesinde "Login sayfası bug'ı" başlıklı yeni bir bug issue'sı oluştur
```

**Analiz Yapma:**
```
@jira PROJ projesindeki son 30 gündeki tüm bug'ları analiz et ve rapor hazırla
```

### 🎯 Cursor AI Agent Yetenekleri

#### **Otomatik Issue Analizi**
- Bug pattern detection
- Performance issue identification
- Code quality assessment
- Security vulnerability analysis

#### **Kod-Issue Bağlantısı**
- Commit message'larından issue referansı
- Branch naming convention'dan issue tracking
- PR description'dan issue linking

#### **Akıllı Issue Oluşturma**
- Code analysis'e dayalı issue generation
- Automated test case creation
- Documentation gap identification

---

## Kullanım Senaryoları

### 🔧 Geliştirici Senaryoları

#### **Scenario 1: Bug Raporu ve Analizi**
```markdown
Cursor Prompt:
"Projemizdeki authentication modülünde bulunan bug'ları Jira'da ara ve analiz et. 
Benzer pattern'leri tespit et ve çözüm önerileri sun."

Beklenen Çıktı:
- Jira'da authentication ile ilgili bug'ların listesi
- Pattern analizi ve kategorilendirme
- Çözüm önerileri ve priority belirleme
- Yeni issue oluşturma önerileri
```

#### **Scenario 2: Feature Development Planning**
```markdown
Cursor Prompt:
"Yeni user management feature'ı için Jira'da epic ve alt task'ları oluştur. 
Gereksinimler dokümanına göre story'leri böl ve estimate ver."

Beklenen Çıktı:
- Epic oluşturma
- User story'leri alt task'lara bölme
- Story point estimation
- Sprint planning önerileri
```

#### **Scenario 3: Code Review ve Quality Assurance**
```markdown
Cursor Prompt:
"Bu PR'daki değişiklikleri analiz et ve ilgili Jira issue'larını güncelle. 
Test coverage raporu hazırla ve QA checklist'i oluştur."

Beklenen Çıktı:
- Issue'ların otomatik güncellenmesi
- Test coverage analizi
- QA checklist oluşturma
- Documentation update önerileri
```

### 📊 Proje Yönetimi Senaryoları

#### **Scenario 4: Sprint Planning ve Tracking**
```markdown
Cursor Prompt:
"Gelecek sprint için backlog'u analiz et ve capacity planning yap. 
Team member'ların workload'unu dengele ve dependency'leri tespit et."

Beklenen Çıktı:
- Backlog analysis
- Capacity planning
- Workload balancing
- Dependency mapping
```

#### **Scenario 5: Release Planning**
```markdown
Cursor Prompt:
"v2.0 release'i için tüm feature'ları ve bug'ları analiz et. 
Release notes hazırla ve deployment checklist'i oluştur."

Beklenen Çıktı:
- Release scope analysis
- Feature completion tracking
- Bug impact assessment
- Release notes generation
```

### 🔍 Analiz ve Raporlama Senaryoları

#### **Scenario 6: Performance Monitoring**
```markdown
Cursor Prompt:
"Son 3 aydaki performance issue'larını analiz et ve trend'leri tespit et. 
Proactive önlemler öner ve monitoring stratejisi hazırla."

Beklenen Çıktı:
- Performance trend analysis
- Issue pattern identification
- Proactive measure suggestions
- Monitoring strategy
```

---

## Analiz ve Raporlama

### 📈 Jira Data Analysis Capabilities

#### **Issue Metrics**
```javascript
// Cursor'un analiz edebileceği metrikler
{
  "issueCount": "Toplam issue sayısı",
  "resolutionTime": "Ortalama çözüm süresi",
  "bugRate": "Bug oranı",
  "reopenRate": "Yeniden açılma oranı",
  "cycleTime": "Cycle time analizi",
  "leadTime": "Lead time analizi"
}
```

#### **Team Performance**
```javascript
// Team analizi
{
  "velocity": "Sprint velocity",
  "burndown": "Burndown chart data",
  "workload": "Team member workload",
  "efficiency": "Team efficiency metrics",
  "collaboration": "Collaboration patterns"
}
```

#### **Quality Metrics**
```javascript
// Quality analysis
{
  "defectDensity": "Defect density",
  "testCoverage": "Test coverage correlation",
  "codeQuality": "Code quality impact",
  "customerSatisfaction": "Customer satisfaction metrics"
}
```

### 📊 Automated Report Generation

#### **Weekly Status Report**
```markdown
Cursor Template:
"Bu hafta için status report hazırla:
- Completed stories
- In-progress tasks
- Blocked issues
- Upcoming deadlines
- Risk assessment"
```

#### **Monthly Trend Analysis**
```markdown
Cursor Template:
"Aylık trend analizi:
- Issue creation vs resolution
- Team velocity changes
- Bug trend analysis
- Feature delivery rate
- Client feedback integration"
```

#### **Release Readiness Report**
```markdown
Cursor Template:
"Release readiness assessment:
- Feature completeness
- Bug severity analysis
- Test execution status
- Documentation completeness
- Deployment readiness"
```

---

## Troubleshooting

### 🔧 Common Issues ve Çözümleri

#### **Authentication Problems**
```bash
# Problem: 401 Unauthorized
# Çözüm: API token'ı kontrol edin
curl -u your-email@company.com:your-api-token \
  https://your-domain.atlassian.net/rest/api/3/myself
```

#### **Connection Issues**
```bash
# Problem: Connection timeout
# Çözüm: Network ve firewall ayarlarını kontrol edin
ping your-domain.atlassian.net
nslookup your-domain.atlassian.net
```

#### **Permission Errors**
```bash
# Problem: 403 Forbidden
# Çözüm: Jira permissions'ları kontrol edin
# Project settings > Permissions > Browse Projects
```

### 🔍 Debug Mode

#### MCP Server Debug
```json
{
  "env": {
    "MCP_VERBOSE": "true",
    "DEBUG": "jira-mcp:*",
    "LOG_LEVEL": "debug"
  }
}
```

#### Cursor Debug
```bash
# Cursor console'da
console.log("MCP Debug info:", mcpDebugInfo);
```

---

## Örnek Komutlar

### 🚀 Cursor ile Jira Komutları

#### **Issue Management**
```
# Issue arama
@jira "PROJ projesinde status=Open olan tüm issue'ları listele"

# Issue oluşturma
@jira "PROJ projesinde 'API performance optimization' başlıklı task oluştur"

# Issue güncelleme
@jira "PROJ-123 issue'sını In Progress durumuna geçir"

# Yorum ekleme
@jira "PROJ-123 issue'sına 'Development completed, ready for testing' yorumu ekle"
```

#### **Analysis Commands**
```
# Trend analizi
@jira "Son 30 gündeki bug trend'ini analiz et ve grafik oluştur"

# Team performance
@jira "Team'in son sprint'teki performance'ını analiz et"

# Code correlation
@jira "Bu repository'deki son commit'leri ilgili Jira issue'larıyla eşleştir"
```

#### **Reporting Commands**
```
# Sprint report
@jira "Aktif sprint için progress report hazırla"

# Release notes
@jira "v2.1.0 release'i için release notes oluştur"

# Bug analysis
@jira "Critical bug'ları öncelik sırasına göre listele ve impact analysis yap"
```

### 📝 Advanced Use Cases

#### **Automated Workflow**
```javascript
// Cursor ile otomatik workflow
async function automatedWorkflow() {
  // 1. Code analysis
  const codeIssues = await analyzeCode();
  
  // 2. Jira issue creation
  const jiraIssues = await createJiraIssues(codeIssues);
  
  // 3. Assignment based on expertise
  await assignIssues(jiraIssues);
  
  // 4. Sprint planning
  await planSprint(jiraIssues);
  
  // 5. Notification
  await notifyTeam(jiraIssues);
}
```

#### **Custom Reports**
```javascript
// Custom report generation
async function generateCustomReport() {
  const data = await fetchJiraData();
  const analysis = await analyzeWithAI(data);
  const report = await generateReport(analysis);
  return report;
}
```

---

## 🎯 Best Practices

### Development Workflow
1. **Issue-driven development**: Her kod değişikliği bir Jira issue'sı ile bağlantılı
2. **Automated linking**: Commit message'larda issue referansı
3. **Continuous integration**: CI/CD pipeline'da Jira integration
4. **Code review**: PR'larda ilgili issue'ların güncellenmesi

### Quality Assurance
1. **Test coverage**: Issue'lar için test case'lerin tanımlanması
2. **Bug tracking**: Bug'ların root cause analysis'i
3. **Performance monitoring**: Performance issue'larının proactive takibi
4. **Documentation**: Issue'lar için detaylı documentation

### Team Collaboration
1. **Standup meetings**: Daily standup'larda Jira issue'ları review
2. **Sprint planning**: Jira data'ya dayalı sprint planning
3. **Retrospectives**: Jira metrics'e dayalı retrospective analysis
4. **Knowledge sharing**: Issue'lardaki knowledge'ın team ile paylaşımı

---

## 🔮 Future Enhancements

### Planned Features
- **Advanced AI Analysis**: Machine learning ile issue pattern detection
- **Predictive Analytics**: Issue resolution time prediction
- **Integration Expansion**: Daha fazla tool ile entegrasyon
- **Custom Workflows**: Kullanıcı tanımlı workflow'lar
- **Real-time Collaboration**: Gerçek zamanlı collaboration features

### Community Contributions
- **Plugin Development**: Custom plugin'ler için framework
- **Template Sharing**: Issue template'leri paylaşım platformu
- **Best Practice Guides**: Community-driven best practice'ler
- **Integration Examples**: Farklı tool'lar için integration örnekleri

---

## 📚 Resources

### Documentation
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Jira REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
- [Cursor AI Documentation](https://cursor.sh/docs)

### Community
- [MCP Discord Server](https://discord.gg/mcp)
- [Jira Community](https://community.atlassian.com/t5/Jira/ct-p/jira)
- [Cursor Community](https://cursor.sh/community)

### Examples
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Jira MCP Examples](https://github.com/cosmix/jira-mcp)
- [Cursor MCP Integration Examples](https://github.com/cursor-examples/mcp)

---

*Bu dokümantasyon, Cursor AI'nın Jira ile MCP protokolü üzerinden entegrasyonunu sağlamak için hazırlanmıştır. Sürekli güncellenecek ve community feedback'lerine göre geliştirilecektir.*

**Son güncelleme**: 2024-12-20
**Versiyon**: 1.0
**Yazar**: AI Assistant
**Lisans**: MIT