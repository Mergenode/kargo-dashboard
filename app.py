import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from faker import Faker
import random

# Sayfa başlığı ve yapılandırma
st.set_page_config(page_title="Kargo Takip Dashboard", layout="wide")
st.title("📦 Kargo Takip Dashboard")

# Veritabanı bağlantısı
conn = sqlite3.connect("kargo_takip.db")
cursor = conn.cursor()

# Tabloyu oluştur (yoksa)
cursor.execute('''
CREATE TABLE IF NOT EXISTS kargo_gonderileri (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gonderen_adi TEXT,
    alici_adi TEXT,
    gonderilen_sehir TEXT,
    durum TEXT
)
''')
conn.commit()

# Veri yoksa sahte veri ekle
cursor.execute("SELECT COUNT(*) FROM kargo_gonderileri")
if cursor.fetchone()[0] == 0:
    faker = Faker()
    sehirler = ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya']
    durumlar = ['Yolda', 'Teslim Edildi', 'Beklemede']
    for _ in range(50):
        cursor.execute('''
            INSERT INTO kargo_gonderileri (gonderen_adi, alici_adi, gonderilen_sehir, durum)
            VALUES (?, ?, ?, ?)
        ''', (
            faker.name(),
            faker.name(),
            random.choice(sehirler),
            random.choice(durumlar)
        ))
    conn.commit()

# Veriyi oku
df = pd.read_sql_query("SELECT * FROM kargo_gonderileri", conn)

# ---------------------- Özet Kutuları -------------------------
st.subheader("📊 Özet Bilgiler")
col1, col2, col3 = st.columns(3)
col1.metric("Toplam Gönderi", len(df))
col2.metric("Teslim Edilen", df[df["durum"] == "Teslim Edildi"].shape[0])
col3.metric("Yolda", df[df["durum"] == "Yolda"].shape[0])

# ---------------------- Şehre Göre Grafik -------------------------
st.subheader("📍 Şehirlere Göre Gönderi Sayısı")
city_counts = df["gonderilen_sehir"].value_counts()
fig1, ax1 = plt.subplots()
city_counts.plot(kind="bar", ax=ax1, color='skyblue')
ax1.set_ylabel("Gönderi Sayısı")
ax1.set_xlabel("Şehir")
st.pyplot(fig1)

# ---------------------- Duruma Göre Grafik -------------------------
st.subheader("🚚 Gönderi Durumlarına Göre Dağılım")
durum_counts = df["durum"].value_counts()
fig2, ax2 = plt.subplots()
durum_counts.plot(kind="pie", autopct='%1.1f%%', ax=ax2, startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
ax2.axis("equal")
st.pyplot(fig2)

# ---------------------- Gönderi Listesi -------------------------
st.subheader("📋 Tüm Gönderiler")
st.dataframe(df)

# ---------------------- CSV İndir -------------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Veriyi CSV Olarak İndir",
    data=csv,
    file_name='kargo_takip.csv',
    mime='text/csv',
)
