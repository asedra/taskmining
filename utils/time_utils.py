"""
Zaman ile ilgili yardımcı fonksiyonlar
"""

import datetime
import time

def get_current_timestamp():
    """
    Geçerli zamanı ISO 8601 formatında döndürür
    
    Returns:
        str: ISO 8601 formatında tarih-saat
    """
    return datetime.datetime.now().isoformat()

def get_current_date():
    """
    Geçerli tarihi YYYY-MM-DD formatında döndürür
    
    Returns:
        str: YYYY-MM-DD formatında tarih
    """
    return datetime.date.today().strftime("%Y-%m-%d")

def parse_timestamp(timestamp_str):
    """
    ISO 8601 formatındaki zaman damgasını datetime nesnesine dönüştürür
    
    Args:
        timestamp_str: ISO 8601 formatında zaman damgası
        
    Returns:
        datetime: Dönüştürülen datetime nesnesi
    """
    return datetime.datetime.fromisoformat(timestamp_str)

def format_duration(seconds):
    """
    Saniye cinsinden süreyi saat:dakika:saniye formatına dönüştürür
    
    Args:
        seconds: Toplam saniye
        
    Returns:
        str: HH:MM:SS formatında süre
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def calculate_time_difference(start_timestamp, end_timestamp):
    """
    İki zaman damgası arasındaki farkı saniye cinsinden hesaplar
    
    Args:
        start_timestamp: Başlangıç zaman damgası (ISO 8601)
        end_timestamp: Bitiş zaman damgası (ISO 8601)
        
    Returns:
        float: Saniye cinsinden zaman farkı
    """
    start_time = parse_timestamp(start_timestamp)
    end_time = parse_timestamp(end_timestamp)
    return (end_time - start_time).total_seconds()

def get_day_of_week(date_str=None):
    """
    Belirtilen veya geçerli tarihin haftanın hangi günü olduğunu döndürür
    
    Args:
        date_str: YYYY-MM-DD formatında tarih (None ise bugün)
        
    Returns:
        str: Haftanın günü (Pazartesi, Salı, vb.)
    """
    days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    
    if date_str:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        date_obj = datetime.date.today()
        
    # Python'da 0=Pazartesi, 6=Pazar
    return days[date_obj.weekday()]

def is_working_hours(timestamp=None):
    """
    Belirtilen veya geçerli zamanın çalışma saatleri içinde olup olmadığını kontrol eder
    (Varsayılan olarak 09:00-18:00 arası çalışma saati kabul edilir)
    
    Args:
        timestamp: ISO 8601 formatında zaman damgası (None ise şu an)
        
    Returns:
        bool: Çalışma saatleri içinde ise True
    """
    if timestamp:
        dt = parse_timestamp(timestamp)
    else:
        dt = datetime.datetime.now()
        
    # Hafta sonu kontrolü
    if dt.weekday() >= 5:  # 5=Cumartesi, 6=Pazar
        return False
        
    # Saat kontrolü (9:00 - 18:00)
    return 9 <= dt.hour < 18 