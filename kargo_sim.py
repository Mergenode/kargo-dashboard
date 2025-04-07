import sqlite3
import pandas as pd
from datetime import datetime
from faker import Faker
import random
import uuid

# Simülasyon için veri oluşturma fonksiyonu (önceki gibi)
def generate_fake_shipments(num_shipments=10):
    cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Gaziantep"]
    statuses = ["Yola çıktı", "Dağıtım merkezinde", "Teslim ediliyor", "Teslim edildi"]
    all_records = []

    for _ in range(num_shipments):
        shipment_id = str(uuid.uuid4())[:8]
        start_city = random.choice(cities)
        end_city = random.choice([c for c in cities if c != start_city])
        days_to_deliver = random.randint(2, 5)
        current_date = datetime.now() - pd.to_timedelta(days_to_deliver, unit='d')
        
        for day in range(days_to_deliver + 1):
            location = random.choice(cities)
            status = statuses[min(day, len(statuses)-1)]
            all_records.append({
                "shipment_id": shipment_id,
                "date": current_date.strftime("%Y-%m-%d"),
                "location": location,
                "status": status,
                "from_city": start_city,
                "to_city": end_city
            })
            current_date += pd.to_timedelta(1, unit='d')
    return pd.DataFrame(all_records)

# Veri üret
df = generate_fake_shipments(20)

# SQLite'e bağlan
conn = sqlite3.connect("kargo_takip.db")
cursor = conn.cursor()

# Tablo oluştur (varsa önce silip yeniden oluştur)
cursor.execute("DROP TABLE IF EXISTS kargo")
cursor.execute("""
    CREATE TABLE kargo (
        shipment_id TEXT,
        date TEXT,
        location TEXT,
        status TEXT,
        from_city TEXT,
        to_city TEXT
    )
""")

# Verileri ekle
df.to_sql("kargo", conn, if_exists='append', index=False)

# Kontrol için birkaç satır getir
for row in cursor.execute("SELECT * FROM kargo LIMIT 5"):
    print(row)

conn.commit()
conn.close()
