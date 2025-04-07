import streamlit as st
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Kargo Takip Paneli", layout="wide")
st.title("📦 Kargo Takip Dashboard")

# Veritabanından veri çek
@st.cache_data
def load_data():
    conn = sqlite3.connect("kargo_takip.db")
    df = pd.read_sql_query("SELECT * FROM kargo", conn)
    conn.close()
    return df

df = load_data()

# --- FİLTRELER ---
st.sidebar.header("🔍 Filtreleme Seçenekleri")

# Şehir filtresi
cities = sorted(df["from_city"].unique())
selected_city = st.sidebar.selectbox("Gönderim Şehri Seç", ["Tümü"] + cities)

# Durum filtresi
statuses = sorted(df["status"].unique())
selected_status = st.sidebar.selectbox("Kargo Durumu Seç", ["Tümü"] + statuses)

# Filtreyi uygula
filtered_df = df.copy()
if selected_city != "Tümü":
    filtered_df = filtered_df[filtered_df["from_city"] == selected_city]
if selected_status != "Tümü":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]

# --- METRİKLER ---
st.metric("📦 Gösterilen Gönderi Sayısı", filtered_df["shipment_id"].nunique())
teslim_sureleri = filtered_df.groupby("shipment_id")["date"].nunique()
ortalama_sure = teslim_sureleri.mean()
st.metric("⏱️ Ortalama Teslim Süresi (gün)", f"{ortalama_sure:.2f}" if not pd.isna(ortalama_sure) else "Veri yok")

# --- GRAFİKLER ---
# 1. Kargo durumları
st.subheader("Durumlara Göre Kargo Sayısı")
fig1, ax1 = plt.subplots()
sns.countplot(data=filtered_df, x="status", order=filtered_df["status"].value_counts().index, ax=ax1)
ax1.set_xlabel("Durum")
ax1.set_ylabel("Adet")
ax1.set_title("📌 Kargo Durumları")
st.pyplot(fig1)

# 2. Gönderim şehirleri
st.subheader("Gönderim Yapılan Şehirler")
fig2, ax2 = plt.subplots()
sns.countplot(data=filtered_df, x="from_city", order=filtered_df["from_city"].value_counts().index, ax=ax2)
ax2.set_title("🚚 Gönderim Şehirleri")
ax2.set_xlabel("Şehir")
ax2.set_ylabel("Adet")
st.pyplot(fig2)

# 3. Teslim süresi dağılımı
st.subheader("Teslim Süresi Dağılımı (Gün)")
fig3, ax3 = plt.subplots()
sns.histplot(teslim_sureleri, bins=range(1, 10), kde=True, ax=ax3)
ax3.set_xlabel("Teslim Süresi (gün)")
ax3.set_ylabel("Kargo Sayısı")
st.pyplot(fig3)
