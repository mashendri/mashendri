# Google Play Store Review Analysis 📊

Sebuah alat analisis sentimen dan NLP untuk ulasan aplikasi di Google Play Store. Proyek ini mencakup scraper data, prapemrosesan teks (NLP), dan dashboard interaktif menggunakan Streamlit.

## ✨ Fitur Utama
- **Scraping Otomatis**: Mengambil ulasan secara real-time berdasarkan App ID dan rentang tahun.
- **Analisis Sentimen**: Klasifikasi sentimen (Positif, Negatif, Netral) menggunakan metode Leksikon dan verifikasi AI (IndoBERT).
- **Dashboard Interaktif**: Visualisasi tren mingguan, distribusi sentimen, dan Word Cloud kata kunci.
- **Deteksi Anomali**: Mengidentifikasi kontradiksi antara rating bintang dan isi teks ulasan.
- **Download Data**: Mengekspor hasil analisis ke format CSV.

## 🛠️ Persyaratan
- Python 3.9+
- Pip (Manajer paket Python)

## 🚀 Cara Menjalankan di Lokal

### 1. Persiapan Lingkungan
Clone repositori ini atau masuk ke direktori proyek, lalu buat virtual environment:

```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
# Untuk Mac/Linux:
source venv/bin/activate
# Untuk Windows:
# venv\Scripts\activate
```

### 2. Instalasi Dependensi
Instal semua pustaka yang diperlukan:

```bash
pip install -r requirements.txt
```

### 3. Menjalankan Analisis
Anda memiliki tiga komponen utama yang dapat dijalankan secara terpisah:

Jalankan `scraper.py` untuk mengambil data ulasan terbaru (secara default mengambil data ulasan tahun sebelumnya):
```bash
python3 scraper.py
```

#### B. Proses Data (NLP & Sentimen)
Jalankan `preprocess.py` untuk membersihkan teks dan menganalisis sentimen dari hasil file CSV scraper:
```bash
python3 preprocess.py
```

#### C. Jalankan Dashboard Streamlit
Jalankan dashboard untuk melihat visualisasi data:
```bash
streamlit run app.py
```
Setelah dijalankan, buka browser di alamat `http://localhost:8501`.

## 📂 Struktur Proyek
- `app.py`: File utama untuk dashboard Streamlit.
- `scraper.py`: Script untuk mengambil data dari Google Play Store.
- `preprocess.py`: Kumpulan fungsi untuk membersihkan teks dan analisis sentimen.
- `requirements.txt`: Daftar pustaka Python yang dibutuhkan.
- `playstore_reviews_*.csv`: File data mentah hasil scraping.
- `processed_playstore_reviews_*.csv`: File data yang sudah diproses oleh NLP.

## 🧰 Teknologi yang Digunakan
- **Python**: Bahasa pemrograman utama.
- **Streamlit**: Framework untuk dashboard data.
- **Pandas**: Manipulasi dan analisis data.
- **Google Play Scraper**: Libraries untuk scraping data.
- **IndoBERT (Transformers)**: Model AI untuk analisis sentimen bahasa Indonesia yang mendalam.
- **NLTK**: Pemrosesan bahasa alami (Stopwords, Tokenization).
- **Matplotlib & WordCloud**: Visualisasi data.

---
Dikembangkan dengan ❤️ untuk eksplorasi data ulasan aplikasi.
