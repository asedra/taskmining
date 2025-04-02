"""
Veritabanı içeriğini kontrol etmek için basit bir script
"""

import sqlite3
import os

def print_table_contents(conn, table_name):
    """Bir tablonun içeriğini yazdırır"""
    print(f"\n=== {table_name} Tablosu ===")
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 10")
        rows = cursor.fetchall()
        
        if not rows:
            print("Tablo boş.")
            return
            
        # Sütun adlarını al
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Sütun adlarını yazdır
        print(" | ".join(columns))
        print("-" * 100)
        
        # Satırları yazdır
        for row in rows:
            print(" | ".join(str(cell) for cell in row))
            
        # Satır sayısını al
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\nToplam kayıt sayısı: {count}")
        
    except sqlite3.Error as e:
        print(f"Hata: {e}")

def main():
    """Ana işlev"""
    db_path = "data/activity.db"
    
    if not os.path.exists(db_path):
        print(f"Veritabanı dosyası bulunamadı: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    
    # Tablo listesini al
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    
    print(f"Veritabanında bulunan tablolar: {', '.join(tables)}")
    
    # Her tablonun içeriğini yazdır
    for table in tables:
        print_table_contents(conn, table)
        
    conn.close()

if __name__ == "__main__":
    main() 