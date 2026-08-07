import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import random

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="Dashboard Sentimen Mie Gacoan", page_icon="🍜", layout="wide")

# ==========================================
# 2. FUNGSI CACHING DATA (Biar loading cepat)
# ==========================================
@st.cache_data
def load_data():
    # Pastikan nama file CSV sesuai dengan file hasil prediksimu
    df = pd.read_csv("gacoan_depok_prediksi.csv") 
    
    # Konversi kolom Tanggal_Ulasan ke format datetime
    df['Tanggal_Ulasan'] = pd.to_datetime(df['Tanggal_Ulasan'])
    return df

# Load data ke dalam memori
df = load_data()

# ==========================================
# 3. HEADER & FILTER UTAMA (DROPDOWN CABANG)
# ==========================================
st.title("📊 Dashboard Analisis Sentimen Mie Gacoan Depok")
st.write("Visualisasi interaktif hasil klasifikasi sentimen ulasan pelanggan Mie Gacoan menggunakan model IndoBERT.")

st.markdown("---")

# Filter Cabang Utama
daftar_cabang = ["Semua Cabang"] + list(df['Cabang'].unique())
pilih_cabang = st.selectbox("🎯 Pilih Cabang Restoran:", daftar_cabang)

# Terapkan filter data berdasarkan pilihan cabang
if pilih_cabang == "Semua Cabang":
    df_filter = df
else:
    df_filter = df[df['Cabang'] == pilih_cabang]

# ==========================================
# 4. KARTU ANGKA RINGKASAN (KEY METRICS)
# ==========================================
total_ulasan = len(df_filter)
total_positif = len(df_filter[df_filter['Label_Prediksi'] == 'Positif'])
total_negatif = len(df_filter[df_filter['Label_Prediksi'] == 'Negatif'])

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Total Ulasan Dianalisis", f"{total_ulasan:,}")
col_m2.metric("Sentimen Positif 😃", f"{total_positif:,}")
col_m3.metric("Sentimen Negatif 😡", f"{total_negatif:,}")

st.markdown("---")

# ==========================================
# 5. BARIS 1: PIE CHART & LINE CHART TREN
# ==========================================
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader(f"Distribusi Sentimen ({pilih_cabang})")
    st.caption("Diagram lingkaran ini menampilkan perbandingan proporsi persentase antara ulasan bersentimen Positif dan Negatif.")
    fig_pie = px.pie(
        df_filter, 
        names='Label_Prediksi', 
        color='Label_Prediksi', 
        color_discrete_map={'Positif':'#2ca02c', 'Negatif':'#d32f2f'},
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.subheader(f"Tren Sentimen Berdasarkan Waktu ({pilih_cabang})")
    st.caption("Grafik garis ini memetakan fluktuasi volume ulasan Positif dan Negatif dari waktu ke waktu berdasarkan tanggal publikasi ulasan.")
    # Mengelompokkan data berdasarkan Tanggal_Ulasan
    df_trend = df_filter.groupby([df_filter['Tanggal_Ulasan'].dt.date, 'Label_Prediksi']).size().reset_index(name='Jumlah')
    fig_line = px.line(
        df_trend, 
        x='Tanggal_Ulasan', 
        y='Jumlah', 
        color='Label_Prediksi',
        color_discrete_map={'Positif':'#2ca02c', 'Negatif':'#d32f2f'},
        markers=True
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# ==========================================
# 6. BARIS 2: WORD CLOUD POSITIF & NEGATIF
# ==========================================
st.subheader(f"🔠 Kata Kunci Utama Ulasan ({pilih_cabang})")
st.caption("Visualisasi Word Cloud di bawah menyoroti kosakata yang paling dominan muncul pada ulasan Positif (kiri) dan Negatif (kanan) untuk memahami topik utama atau faktor kepuasan/keluhan pelanggan.")

col_wc1, col_wc2 = st.columns(2)

# --- Fungsi Warna Custom ---
def warna_positif(word, font_size, position, orientation, random_state=None, **kwargs):
    # Mengembalikan warna hijau dengan tingkat kegelapan acak (20% - 45%)
    return f"hsl(120, 100%, {random.randint(20, 45)}%)" 

def warna_negatif(word, font_size, position, orientation, random_state=None, **kwargs):
    # Mengembalikan warna merah dengan tingkat kegelapan acak (20% - 45%)
    return f"hsl(0, 100%, {random.randint(20, 45)}%)"

# --- Wordcloud Positif ---
with col_wc1:
    st.markdown("#### Ulasan Positif 😃")
    teks_pos = " ".join(df_filter[df_filter['Label_Prediksi'] == 'Positif']['Teks_Bersih'].dropna().astype(str).tolist())
    
    if teks_pos.strip():
        with st.spinner("Merender Word Cloud Positif..."):
            wc_pos = WordCloud(
                width=600, height=350, 
                background_color='white', 
                colormap='Greens', 
                max_words=100,
                random_state=42,
                color_func=warna_positif
            ).generate(teks_pos)
            
            fig_pos, ax_pos = plt.subplots(figsize=(6, 3.5))
            ax_pos.imshow(wc_pos, interpolation='bilinear')
            ax_pos.axis("off")
            st.pyplot(fig_pos)
    else:
        st.info("Tidak ada data ulasan positif untuk cabang ini.")

# --- Wordcloud Negatif ---
with col_wc2:
    st.markdown("#### Ulasan Negatif 😡")
    teks_neg = " ".join(df_filter[df_filter['Label_Prediksi'] == 'Negatif']['Teks_Bersih'].dropna().astype(str).tolist())
    
    if teks_neg.strip():
        with st.spinner("Merender Word Cloud Negatif..."):
            wc_neg = WordCloud(
                width=600, height=350, 
                background_color='white', 
                colormap='Reds', 
                max_words=100,
                random_state=42,
                color_func=warna_negatif
            ).generate(teks_neg)
            
            fig_neg, ax_neg = plt.subplots(figsize=(6, 3.5))
            ax_neg.imshow(wc_neg, interpolation='bilinear')
            ax_neg.axis("off")
            st.pyplot(fig_neg)
    else:
        st.info("Tidak ada data ulasan negatif untuk cabang ini.")

st.markdown("---")

st.markdown("---")

# ==========================================
# 7. BARIS 3: CONTOH HASIL PREDIKSI MODEL (TABEL DATA)
# ==========================================
st.subheader(f"📄 Contoh Hasil Prediksi Model ({pilih_cabang})")
st.caption("Tabel berikut menyajikan sampel acak teks ulasan pelanggan beserta label hasil prediksi sentimen yang telah diklasifikasikan secara otomatis oleh model IndoBERT.")
# Memilih kolom yang relevan untuk ditampilkan
if 'Teks_Ulasan' in df_filter.columns:
    kolom_tampil = ['Cabang', 'Tanggal_Ulasan', 'Teks_Ulasan', 'Label_Prediksi']
else:
    kolom_tampil = ['Cabang', 'Tanggal_Ulasan', 'Teks_Bersih', 'Label_Prediksi']

# Membuat salinan data khusus untuk tabel agar tidak merusak data grafik
df_tampil = df_filter[kolom_tampil].copy()

df_tampil['Tanggal_Ulasan'] = df_tampil['Tanggal_Ulasan'].dt.strftime('%Y-%m-%d')

# Mengambil sampel acak (maksimal 100 baris, atau sesuai jumlah data jika kurang dari 100)
jumlah_sampel = min(100, len(df_tampil))
df_sampel = df_tampil.sample(n=jumlah_sampel)

# Menampilkan dataframe
st.dataframe(
    df_sampel, 
    use_container_width=True, 
    hide_index=True
)