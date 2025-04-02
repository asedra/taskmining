"""
Ekran görüntüsü ve aksiyon ilişkisini kontrol eden script
"""

from activity_logger import ActivityLogger
import os
from PIL import Image
import webbrowser

def display_event_with_screenshot(event):
    """
    Olay ve ekran görüntüsünü gösterir
    
    Args:
        event: (timestamp, window_title, application, event_type, event_details, screenshot_path)
    """
    timestamp, window_title, application, event_type, event_details, screenshot_path = event
    
    print("\n" + "="*50)
    print(f"Zaman: {timestamp}")
    print(f"Pencere: {window_title}")
    print(f"Uygulama: {application}")
    print(f"Olay Türü: {event_type}")
    print(f"Detaylar: {event_details}")
    print(f"Ekran Görüntüsü: {screenshot_path}")
    
    if os.path.exists(screenshot_path):
        print("\nEkran görüntüsü mevcut.")
        # Ekran görüntüsünü varsayılan görüntüleyici ile aç
        webbrowser.open(screenshot_path)
    else:
        print("\nEkran görüntüsü bulunamadı!")
    print("="*50)

def main():
    logger = ActivityLogger()
    
    print("\nSon 10 ekran görüntüsü ve olay:")
    events = logger.get_events_with_screenshots(limit=10)
    for event in events:
        display_event_with_screenshot(event)
    
    print("\nSon 5 klavye olayı ve ekran görüntüleri:")
    keyboard_events = logger.get_event_screenshot_pairs(event_type="keyboard", limit=5)
    for event in keyboard_events:
        display_event_with_screenshot(event)
    
    print("\nSon 5 fare tıklaması ve ekran görüntüleri:")
    mouse_events = logger.get_event_screenshot_pairs(event_type="mouse_click", limit=5)
    for event in mouse_events:
        display_event_with_screenshot(event)

if __name__ == "__main__":
    main() 