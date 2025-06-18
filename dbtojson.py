import sqlite3
import json
from datetime import datetime

def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

def db_to_json():
    # Veritabanı bağlantısı
    conn = sqlite3.connect('araclar.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Tüm tabloları al
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    data = {}
    
    # Her tablo için verileri al
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()
        
        # Tablo verilerini listeye dönüştür
        table_data = [dict(row) for row in rows]
        data[table_name] = table_data
    
    conn.close()
    
    # JSON dosyasına kaydet
    with open('veritabani.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, default=datetime_handler)
    
    print('Veritabanı başarıyla JSON formatına dönüştürüldü.')

if __name__ == '__main__':
    db_to_json()