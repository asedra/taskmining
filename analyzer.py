"""
Task Mining Analiz Modülü
Bu modül, toplanan kullanıcı aktivite verilerini analiz eder ve raporlar oluşturur.
"""

import os
import sqlite3
import pandas as pd
import datetime
import json
from collections import Counter, defaultdict
import matplotlib
# Matplotlib'i GUI olmadan çalışacak şekilde ayarla (thread-safe)
matplotlib.use('Agg')  # GUI olmadan çalışacak backend
import matplotlib.pyplot as plt
from utils.time_utils import format_duration

class Analyzer:
    def __init__(self, activity_logger=None, db_path=None):
        """
        Args:
            activity_logger: ActivityLogger nesnesi
            db_path: Veritabanı dosya yolu (activity_logger None ise kullanılır)
        """
        if activity_logger:
            self.db_path = activity_logger.db_path
        elif db_path:
            self.db_path = db_path
        else:
            self.db_path = "data/activity.db"
        
        self.reports_dir = "data/reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def _connect_db(self):
        """Veritabanına bağlantı oluşturur"""
        return sqlite3.connect(self.db_path)

    def analyze_app_usage(self, date=None):
        """
        Belirli bir gün için uygulama kullanım sürelerini analiz eder
        
        Args:
            date: İstenen tarih (varsayılan=bugün)
            
        Returns:
            dict: Uygulama isimlerini ve süreleri içeren sözlük
        """
        if date is None:
            date = datetime.date.today().strftime("%Y-%m-%d")
            
        conn = self._connect_db()
        query = "SELECT application, duration_seconds FROM app_usage WHERE date = ?"
        
        df = pd.read_sql_query(query, conn, params=(date,))
        conn.close()
        
        if df.empty:
            return {}
            
        # Uygulamalara göre süreleri topla
        app_usage = df.groupby('application')['duration_seconds'].sum().to_dict()
        
        # Süreleri formatla
        formatted_usage = {app: format_duration(seconds) for app, seconds in app_usage.items()}
        
        return formatted_usage

    def identify_frequent_sequences(self, days=7, min_frequency=3):
        """
        Sık tekrarlanan aktivite dizilerini tanımlar
        
        Args:
            days: Kaç gün öncesine kadar bakılacağı
            min_frequency: Minimum tekrar sayısı
            
        Returns:
            list: Tekrarlanan diziler ve tekrar sayıları
        """
        conn = self._connect_db()
        
        # Son X günlük window değişikliklerini al
        cutoff_date = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        query = """
        SELECT timestamp, application, window_title 
        FROM user_events 
        WHERE event_type = 'window_change' AND timestamp >= ?
        ORDER BY timestamp
        """
        
        df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        conn.close()
        
        if df.empty:
            return []
        
        # Aktivite dizilerini oluştur (3'lü gruplar halinde)
        sequences = []
        for i in range(len(df) - 2):
            seq = tuple(f"{row['application']}: {row['window_title']}" for _, row in df.iloc[i:i+3].iterrows())
            sequences.append(seq)
        
        # Dizilerin sıklığını say
        sequence_counter = Counter(sequences)
        
        # Minimum sıklıktan fazla olanları al
        frequent_sequences = [
            {"sequence": seq, "frequency": freq}
            for seq, freq in sequence_counter.items()
            if freq >= min_frequency
        ]
        
        # Sıklığa göre sırala
        frequent_sequences.sort(key=lambda x: x["frequency"], reverse=True)
        
        return frequent_sequences

    def analyze_browser_patterns(self, days=7):
        """
        Tarayıcı kullanım desenlerini analiz eder
        
        Args:
            days: Kaç gün öncesine kadar bakılacağı
            
        Returns:
            dict: Tarayıcı kullanım istatistikleri
        """
        conn = self._connect_db()
        
        cutoff_date = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        query = """
        SELECT timestamp, url, title, browser
        FROM browser_events
        WHERE timestamp >= ?
        """
        
        df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        conn.close()
        
        if df.empty:
            return {}
        
        # URL domain'lerini çıkar
        def extract_domain(url):
            try:
                from urllib.parse import urlparse
                return urlparse(url).netloc
            except:
                return url
                
        df['domain'] = df['url'].apply(extract_domain)
        
        # Her tarayıcı için alan adı sıklığını hesapla
        browser_stats = {}
        for browser in df['browser'].unique():
            # Tarayıcıya özgü verileri seç
            browser_data = df[df['browser'] == browser].copy()
            
            # En sık ziyaret edilen 10 domain
            top_domains = browser_data['domain'].value_counts().head(10).to_dict()
            
            # Günlük ortalama ziyaret hesabı (SettingWithCopyWarning'i önlemek için .loc kullanarak)
            browser_data.loc[:, 'date'] = pd.to_datetime(browser_data['timestamp']).dt.date
            daily_visits = browser_data.groupby('date').size()
            avg_daily_visits = daily_visits.mean() if not daily_visits.empty else 0
            
            browser_stats[browser] = {
                "top_domains": top_domains,
                "avg_daily_visits": round(avg_daily_visits, 1)
            }
            
        return browser_stats

    def analyze_file_activities(self, days=7):
        """
        Dosya aktivitelerini analiz eder
        
        Args:
            days: Kaç gün öncesine kadar bakılacağı
            
        Returns:
            dict: Dosya aktivite istatistikleri
        """
        conn = self._connect_db()
        
        cutoff_date = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        query = """
        SELECT timestamp, file_path, event_type
        FROM file_events
        WHERE timestamp >= ?
        """
        
        df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        conn.close()
        
        if df.empty:
            return {}
        
        # Dosya uzantılarını çıkar
        df['extension'] = df['file_path'].apply(lambda x: os.path.splitext(x)[1].lower() if os.path.splitext(x)[1] else 'no_extension')
        
        # Aktivite türüne göre sayıları hesapla
        activity_counts = df['event_type'].value_counts().to_dict()
        
        # En sık değiştirilen dosya uzantıları
        top_extensions = df['extension'].value_counts().head(5).to_dict()
        
        # Günün saatlerine göre aktivite dağılımı
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_activity = df.groupby('hour').size().to_dict()
        
        return {
            "activity_counts": activity_counts,
            "top_extensions": top_extensions,
            "hourly_activity": hourly_activity
        }

    def identify_automation_candidates(self):
        """
        Potansiyel otomasyon adaylarını belirler
        
        Returns:
            list: Potansiyel otomasyon adayları listesi
        """
        # Sık tekrarlanan dizileri bul
        frequent_sequences = self.identify_frequent_sequences()
        
        # Uygulama kullanım sürelerini al
        app_usage = self.analyze_app_usage(date=datetime.date.today().strftime("%Y-%m-%d"))
        
        # Dosya aktivitelerini al
        file_activities = self.analyze_file_activities()
        
        # Otomasyon adaylarını belirle
        candidates = []
        
        # Sık tekrarlanan dizilere dayalı adaylar
        for seq_data in frequent_sequences[:5]:  # En sık 5 dizi
            candidates.append({
                "type": "sequence",
                "description": f"Sık tekrarlanan işlem dizisi: {' -> '.join([s.split(':')[0] for s in seq_data['sequence']])}",
                "frequency": seq_data["frequency"],
                "details": seq_data["sequence"]
            })
        
        # En çok kullanılan uygulamalar
        if app_usage:
            sorted_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)
            for app, duration in sorted_apps[:3]:  # En çok kullanılan 3 uygulama
                candidates.append({
                    "type": "app_usage",
                    "description": f"Yoğun kullanılan uygulama: {app}",
                    "duration": duration,
                    "details": f"{app} uygulaması günde {duration} süre kullanılıyor"
                })
        
        # Dosya aktiviteleri
        if file_activities and "activity_counts" in file_activities:
            for event_type, count in file_activities["activity_counts"].items():
                if count > 10:  # Eşik değeri
                    candidates.append({
                        "type": "file_activity",
                        "description": f"Yoğun dosya aktivitesi: {event_type}",
                        "count": count,
                        "details": f"Son 7 günde {count} adet {event_type} dosya olayı tespit edildi"
                    })
        
        return candidates

    def generate_daily_report(self):
        """
        Günlük analiz raporu oluşturur
        """
        today = datetime.date.today().strftime("%Y-%m-%d")
        report_data = {
            "date": today,
            "app_usage": self.analyze_app_usage(date=today),
            "browser_patterns": self.analyze_browser_patterns(days=1),
            "file_activities": self.analyze_file_activities(days=1),
            "automation_candidates": self.identify_automation_candidates()
        }
        
        # JSON raporu kaydet
        report_file = os.path.join(self.reports_dir, f"daily_report_{today}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # İstatistikleri görselleştir
        self._generate_visualizations(report_data, today)
        
        print(f"Günlük rapor oluşturuldu: {report_file}")

    def generate_weekly_report(self):
        """
        Haftalık analiz raporu oluşturur
        """
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=7)
        
        report_data = {
            "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            "app_usage_trend": {},
            "browser_patterns": self.analyze_browser_patterns(days=7),
            "file_activities": self.analyze_file_activities(days=7),
            "frequent_sequences": self.identify_frequent_sequences(days=7),
            "automation_candidates": self.identify_automation_candidates()
        }
        
        # Son 7 gün için uygulama kullanım trendini hesapla
        conn = self._connect_db()
        query = """
        SELECT date, application, duration_seconds
        FROM app_usage
        WHERE date BETWEEN ? AND ?
        """
        df = pd.read_sql_query(query, conn, params=(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        conn.close()
        
        if not df.empty:
            # Tarihe göre grupla
            pivot_df = df.pivot_table(index='date', columns='application', values='duration_seconds', aggfunc='sum').fillna(0)
            report_data["app_usage_trend"] = pivot_df.to_dict()
        
        # JSON raporu kaydet
        report_file = os.path.join(self.reports_dir, f"weekly_report_{end_date.strftime('%Y-%m-%d')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"Haftalık rapor oluşturuldu: {report_file}")

    def _generate_visualizations(self, report_data, date):
        """
        Rapor verilerine dayalı görselleştirmeler oluşturur
        
        Args:
            report_data: Rapor verisi
            date: Rapor tarihi
        """
        try:
            # Uygulama kullanım süreleri grafiği
            if report_data["app_usage"]:
                plt.figure(figsize=(10, 6))
                apps = list(report_data["app_usage"].keys())
                # Saat:dakika:saniye formatından saniyeye dönüştür
                durations = []
                for duration_str in report_data["app_usage"].values():
                    parts = duration_str.split(':')
                    if len(parts) == 3:
                        hours, minutes, seconds = map(int, parts)
                        total_seconds = hours * 3600 + minutes * 60 + seconds
                        durations.append(total_seconds / 60)  # dakikaya çevir
                
                plt.bar(apps, durations)
                plt.title("Uygulama Kullanım Süreleri (Dakika)")
                plt.xlabel("Uygulamalar")
                plt.ylabel("Süre (Dakika)")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plt.savefig(os.path.join(self.reports_dir, f"app_usage_{date}.png"))
                plt.close()
            
            # Dosya aktiviteleri grafiği
            if report_data["file_activities"] and "activity_counts" in report_data["file_activities"]:
                plt.figure(figsize=(8, 6))
                events = list(report_data["file_activities"]["activity_counts"].keys())
                counts = list(report_data["file_activities"]["activity_counts"].values())
                
                plt.pie(counts, labels=events, autopct='%1.1f%%')
                plt.title("Dosya Aktiviteleri Dağılımı")
                plt.tight_layout()
                plt.savefig(os.path.join(self.reports_dir, f"file_activities_{date}.png"))
                plt.close()
            
            # Tarayıcı aktiviteleri grafiği
            if report_data["browser_patterns"]:
                for browser, data in report_data["browser_patterns"].items():
                    if "top_domains" in data and data["top_domains"]:
                        plt.figure(figsize=(10, 6))
                        domains = list(data["top_domains"].keys())
                        visits = list(data["top_domains"].values())
                        
                        plt.barh(domains, visits)
                        plt.title(f"{browser} - En Çok Ziyaret Edilen Siteler")
                        plt.xlabel("Ziyaret Sayısı")
                        plt.tight_layout()
                        plt.savefig(os.path.join(self.reports_dir, f"{browser}_domains_{date}.png"))
                        plt.close()
        except Exception as e:
            print(f"Görselleştirme oluşturulurken hata: {e}")

if __name__ == "__main__":
    # Tek başına çalıştığında test raporları oluşturur
    analyzer = Analyzer()
    analyzer.generate_daily_report()
    analyzer.generate_weekly_report()
    print("Analiz tamamlandı.") 