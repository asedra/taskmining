"""
Veritabanı kayıtlarını kontrol eden script
"""

from activity_logger import ActivityLogger

def main():
    logger = ActivityLogger()
    
    print("\nuser_events tablosundaki son 10 kayıt:")
    events = logger.get_user_events(limit=10)
    for event in events:
        print("\n" + "="*50)
        print(f"Timestamp: {event[0]}")
        print(f"Window Title: {event[1]}")
        print(f"Application: {event[2]}")
        print(f"Event Type: {event[3]}")
        print(f"Event Details: {event[4]}")
        print(f"Screenshot Path: {event[5]}")
        print(f"Screenshot Filename: {event[6]}")
        print("="*50)
    
    print("\nEkran görüntüsü olan son 10 kayıt:")
    screenshot_events = logger.get_events_with_screenshots(limit=10)
    for event in screenshot_events:
        print("\n" + "="*50)
        print(f"Timestamp: {event[0]}")
        print(f"Window Title: {event[1]}")
        print(f"Application: {event[2]}")
        print(f"Event Type: {event[3]}")
        print(f"Event Details: {event[4]}")
        print(f"Screenshot Path: {event[5]}")
        print("="*50)

if __name__ == "__main__":
    main() 