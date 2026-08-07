import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from wordcloud import WordCloud
import random

# ==========================================
# 1. KONFIGURASI HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="Dashboard Visualisasi Sentimen", page_icon="🍜", layout="wide")

# ==========================================
# 2. FUNGSI CACHING DATA
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv("gacoan_depok_prediksi.csv") 
    
    # Konversi kolom Tanggal_Ulasan ke format datetime
    df['Tanggal_Ulasan'] = pd.to_datetime(df['Tanggal_Ulasan'])
    return df

# Load data ke dalam memori
df = load_data()

# ==========================================
# 3. HEADER & FILTER UTAMA (DROPDOWN CABANG)
# ==========================================
st.title("Dashboard Visualisasi Sentimen Mie Gacoan Cabang Depok")
st.write(
    "Visualisasi interaktif hasil klasifikasi sentimen ulasan pelanggan Mie Gacoan Cabang Depok yang diperoleh dari **Google Maps** dan diklasifikasikan menggunakan model **IndoBERT**."
    )

st.markdown("---")

# Filter Cabang Utama
daftar_cabang = ["Semua Cabang"] + list(df['Cabang'].unique())
st.subheader("🎯 Filter Cabang Restoran")
st.caption("Gunakan dropdown di bawah untuk memilih cabang restoran yang ingin dianalisis. Pilih 'Semua Cabang' untuk melihat data secara keseluruhan.")
pilih_cabang = st.selectbox("Pilih Cabang Restoran:", daftar_cabang)

# Terapkan filter data berdasarkan pilihan cabang
if pilih_cabang == "Semua Cabang":
    df_filter = df
else:
    df_filter = df[df['Cabang'] == pilih_cabang]

st.markdown("---")

# ==========================================
# 4 & 5. RINGKASAN METRICS & PIE CHART
# ==========================================
# Menghitung nilai metrics
total_ulasan = len(df_filter)
total_positif = len(df_filter[df_filter['Label_Prediksi'] == 'Positif'])
total_negatif = len(df_filter[df_filter['Label_Prediksi'] == 'Negatif'])

col_left, col_right = st.columns([1, 1.2])

# --- KOLOM KIRI: Rekapitulasi Numerik ---
with col_left:
    st.subheader(f"📝 Statistik Distribusi Sentimen ({pilih_cabang})")
    st.caption("Rincian kuantitatif total ulasan serta perbandingan numerik antara sentimen Positif dan Negatif.")

    st.markdown("<br>", unsafe_allow_html=True)

    col_total, col_pos, col_neg = st.columns(3)
    with col_total:
        st.metric("Total Ulasan Dianalisis", f"{total_ulasan:,}")
    with col_pos:
        st.metric("Sentimen Positif 😃", f"{total_positif:,}")
    with col_neg:
        st.metric("Sentimen Negatif 😡", f"{total_negatif:,}")

# --- KOLOM KANAN: Pie Chart Visual ---
with col_right:
    st.subheader(f"📊 Visualisasi Distribusi Sentimen ({pilih_cabang})")
    st.caption("Diagram lingkaran ini menampilkan perbandingan proporsi persentase ulasan Positif dan Negatif.")
    
    fig_pie = px.pie(
        df_filter, 
        names='Label_Prediksi', 
        color='Label_Prediksi', 
        color_discrete_map={'Positif':'#2ca02c', 'Negatif':'#d32f2f'},
        hole=0.4,
        height=350
    )
    
    fig_pie.update_layout(
        margin=dict(t=10, b=10, l=10, r=10)
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ==========================================
# 6. TREN SENTIMEN BERDASARKAN WAKTU (LINE CHART)
# ==========================================
st.subheader(f"📈 Tren Sentimen Berdasarkan Waktu ({pilih_cabang})")
st.caption("Grafik garis ini memetakan fluktuasi volume ulasan Positif dan Negatif dari bulan ke bulan berdasarkan tanggal publikasi ulasan.")

if not df_filter.empty and 'Tanggal_Ulasan' in df_filter.columns:
    df_line = df_filter.copy()
    
    # 1. Ekstrak Bulan dan Tahun (Format: YYYY-MM) untuk pengelompokan
    df_line['Bulan_Tahun'] = df_line['Tanggal_Ulasan'].dt.to_period('M')

    # 2. Hitung jumlah tiap label per bulan
    tren_sentimen = df_line.groupby(['Bulan_Tahun', 'Label_Prediksi']).size().unstack(fill_value=0)

    for col in ['Positif', 'Negatif']:
        if col not in tren_sentimen.columns:
            tren_sentimen[col] = 0

    # 3. Ubah indeks kembali ke format Timestamp agar matplotlib bisa membaca urutan waktunya
    tren_sentimen.index = tren_sentimen.index.to_timestamp()

    # 4. Mulai Menggambar Grafik Matplotlib
    fig_line, ax = plt.subplots(figsize=(12, 5))

    # Plot Garis Positif (Warna Hijau)
    ax.plot(
        tren_sentimen.index, tren_sentimen['Positif'],
        marker='o', linestyle='-', linewidth=2, color='#2ca02c', label='Positif'
    )

    # Plot Garis Negatif (Warna Merah)
    ax.plot(
        tren_sentimen.index, tren_sentimen['Negatif'],
        marker='s', linestyle='-', linewidth=2, color='#d32f2f', label='Negatif'
    )

    # 5. Kustomisasi Tampilan Grafik
    ax.set_xlabel('Periode Waktu (Bulan)', fontsize=11, labelpad=10)
    ax.set_ylabel('Jumlah Ulasan', fontsize=11, labelpad=10)

    # Format sumbu X agar rapi (Menampilkan Singkatan Bulan dan Tahun)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)

    ax.legend(title='Sentimen', title_fontsize='11', fontsize=10, loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()

    # Tampilkan grafik Matplotlib di Streamlit
    st.pyplot(fig_line)
else:
    st.info("Data tanggal ulasan tidak tersedia.")

# ==========================================
# 7. WORD CLOUD POSITIF & NEGATIF
# ==========================================
st.subheader(f"🔠 Kata Kunci Utama Sentimen ({pilih_cabang})")
st.caption("Visualisasi Word Cloud di bawah menyoroti kosakata yang paling dominan muncul pada Sentimen Positif (kiri) dan Sentimen Negatif (kanan) untuk memahami topik utama atau faktor kepuasan/keluhan pelanggan.")

col_wc1, col_wc2 = st.columns(2)

# --- Fungsi Warna Custom ---
def warna_positif(word, font_size, position, orientation, random_state=None, **kwargs):
    kegelapan = random_state.randint(15, 45) if random_state else 30
    return f"hsl(120, 100%, {kegelapan}%)"

def warna_negatif(word, font_size, position, orientation, random_state=None, **kwargs):
    kegelapan = random_state.randint(15, 45) if random_state else 30
    return f"hsl(0, 100%, {kegelapan}%)"

# --- Fungsi Membersihkan Stopwords (Khusus WordCloud) ---
stopwords_tambahan = {'dan', 'yang', 'di', 'ke', 'dari', 'untuk', 'dengan', 'ini', 'itu', 'nya', 'ada', 'yg'}

def bersihkan_untuk_wordcloud(teks_panjang):
    words = str(teks_panjang).split()
    # Hanya simpan kata yang tidak ada di dalam stopwords_tambahan
    words = [w for w in words if w.lower() not in stopwords_tambahan]
    return " ".join(words)

# --- Wordcloud Positif ---
with col_wc1:
    st.markdown("#### Sentimen Positif 😃")
    
    # 1. Ambil teks dan gabungkan
    teks_pos_mentah = " ".join(df_filter[df_filter['Label_Prediksi'] == 'Positif']['Teks_Bersih'].dropna().astype(str).tolist())
    
    # 2. Bersihkan kata hubungnya
    teks_pos = bersihkan_untuk_wordcloud(teks_pos_mentah)
    
    if teks_pos.strip():
        with st.spinner("Merender Word Cloud Positif..."):
            wc_pos = WordCloud(
                width=600, height=350, 
                background_color='white', 
                colormap='Greens', 
                max_words=100,
                random_state=32,
                color_func=warna_positif
            ).generate(teks_pos)
            
            fig_pos, ax_pos = plt.subplots(figsize=(6, 3.5))
            ax_pos.imshow(wc_pos, interpolation='bilinear')
            ax_pos.axis("off")
            st.pyplot(fig_pos)
    else:
        st.info("Tidak ada data sentimen positif untuk cabang ini.")

# --- Wordcloud Negatif ---
with col_wc2:
    st.markdown("#### Sentimen Negatif 😡")
    
    # 1. Ambil teks dan gabungkan
    teks_neg_mentah = " ".join(df_filter[df_filter['Label_Prediksi'] == 'Negatif']['Teks_Bersih'].dropna().astype(str).tolist())
    
    # 2. Bersihkan kata hubungnya
    teks_neg = bersihkan_untuk_wordcloud(teks_neg_mentah)
    
    if teks_neg.strip():
        with st.spinner("Merender Word Cloud Negatif..."):
            wc_neg = WordCloud(
                width=600, height=350, 
                background_color='white', 
                colormap='Reds', 
                max_words=100,
                random_state=32,
                color_func=warna_negatif
            ).generate(teks_neg)
            
            fig_neg, ax_neg = plt.subplots(figsize=(6, 3.5))
            ax_neg.imshow(wc_neg, interpolation='bilinear')
            ax_neg.axis("off")
            st.pyplot(fig_neg)
    else:
        st.info("Tidak ada data sentimen negatif untuk cabang ini.")

st.markdown("---")

# ==========================================
# 8. CONTOH HASIL PREDIKSI MODEL (TABEL DATA)
# ==========================================
st.subheader(f"📄 Contoh Hasil Prediksi Model ({pilih_cabang})")
st.caption("Tabel berikut menyajikan sampel acak teks ulasan pelanggan beserta label hasil prediksi sentimen yang telah diklasifikasikan secara otomatis oleh model IndoBERT.")

kolom_tampil = ['Cabang', 'Tanggal_Ulasan', 'Teks_Ulasan', 'Label_Prediksi']

df_tabel = df_filter[kolom_tampil].copy()
df_tabel['Tanggal_Ulasan'] = pd.to_datetime(df_tabel['Tanggal_Ulasan']).dt.strftime('%Y-%m-%d')

jumlah_sampel = min(100, len(df_tabel))
df_tabel_acak = df_tabel.sample(n=jumlah_sampel, random_state=42).reset_index(drop=True)
total_baris = len(df_tabel_acak)

if total_baris > 0:
    baris_per_halaman = 10
    total_halaman = (total_baris // baris_per_halaman) + (1 if total_baris % baris_per_halaman > 0 else 0)

    pilihan_rentang = []
    for i in range(total_halaman):
        awal = (i * baris_per_halaman) + 1
        akhir = min((i + 1) * baris_per_halaman, total_baris)
        pilihan_rentang.append(f"Tampilkan Data ke {awal} - {akhir}")

    rentang_terpilih = st.selectbox("Pilih rentang data:", pilihan_rentang)
    halaman_saat_ini = pilihan_rentang.index(rentang_terpilih)
    indeks_awal = halaman_saat_ini * baris_per_halaman
    indeks_akhir = min(indeks_awal + baris_per_halaman, total_baris)
    
    df_tampil = df_tabel_acak.iloc[indeks_awal:indeks_akhir]
    
    st.dataframe(
        df_tampil, 
        use_container_width=True, 
        hide_index=True 
    )
else:
    st.info("Tidak ada data sentimen untuk cabang ini.")

st.markdown("---")
# ==========================================
# 9. FOOTER
# ==========================================
st.markdown(
    """
    <div style="text-align: center; font-size: 12px; color: gray; line-height: 1.8;">
        <p style="margin: 0; padding: 0;">
            🍜 <strong>Dashboard Analisis Sentimen Mie Gacoan Depok</strong><br>
            Dikembangkan oleh <strong>Zahwa Annisa Hendajani</strong> © 2026<br>
            <em>Dashboard ini dikembangkan sebagai bagian dari Penulisan Ilmiah dengan judul <br>
            "Analisis Sentimen Ulasan Pelanggan Mie Gacoan Cabang Depok Berdasarkan Ulasan Google Maps Menggunakan Metode IndoBERT"</em>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)