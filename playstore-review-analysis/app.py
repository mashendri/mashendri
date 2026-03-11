import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import glob
import os
import datetime
from scraper import scrape_playstore_reviews
from preprocess import preprocess_dataframe, classify_sentiment_indobert

st.set_page_config(page_title="Review Analysis Dashboard", layout="wide")

st.title("📊 Google Play Store Review Analysis")

# Session State Initialization
if 'raw_df' not in st.session_state:
    st.session_state['raw_df'] = None
if 'processed_df' not in st.session_state:
    st.session_state['processed_df'] = None
if 'ai_correction_metrics' not in st.session_state:
    st.session_state['ai_correction_metrics'] = None
# Unused variables removed
if 'app_id' not in st.session_state:
    st.session_state['app_id'] = "com.jago.digitalBanking"
if 'start_year' not in st.session_state:
    st.session_state['start_year'] = 2025

# Sidebar Configuration
@st.cache_resource
def load_sentiment_pipeline():
    from transformers import pipeline
    model_name = "w11wo/indonesian-roberta-base-sentiment-classifier"
    return pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)

st.sidebar.header("⚙️ Konfigurasi Scraping")
with st.sidebar.form(key='scrape_form'):
    app_id = st.text_input("App ID (contoh: com.jago.digitalBanking)", value=st.session_state['app_id'])
    start_year = st.number_input("Tahun Mulai", min_value=2010, max_value=2030, value=st.session_state['start_year'], step=1)
    submit_button = st.form_submit_button(label='1. Ambil Data (Scrape) Baru')

if submit_button:
    st.session_state['app_id'] = app_id
    st.session_state['start_year'] = start_year
    with st.spinner(f"Sedang mengambil data review untuk {app_id} sejak {start_year}..."):
        # Redirect stdout/stderr if needed, but for now we'll just run it
        raw_df = scrape_playstore_reviews(app_id, start_year)
        if raw_df is not None and not raw_df.empty:
            st.session_state['raw_df'] = raw_df
            st.session_state['processed_df'] = None # Reset processed data
            st.session_state['ai_correction_metrics'] = None
            st.sidebar.success(f"Berhasil mengunduh {len(raw_df):,} review!")
        else:
            st.sidebar.error("Gagal mengambil data atau review tidak ditemukan.")

st.sidebar.markdown("---")
st.sidebar.header("📂 Riwayat Data")
# Find all csv files that start with playstore_reviews_
existing_files = glob.glob("playstore_reviews_*.csv")
existing_files = [f for f in existing_files if not f.startswith("processed_")]

if existing_files:
    file_mapping = {}
    for f in existing_files:
        # Expected format: playstore_reviews_com_jago_app_2025.csv
        parts = f.replace("playstore_reviews_", "").replace(".csv", "").rsplit("_", 1)
        if len(parts) == 2:
            app_id_clean = parts[0].replace("_", ".")
            display_name = f"{app_id_clean} (Sejak {parts[1]})"
            file_mapping[display_name] = f
        else:
            file_mapping[f] = f # fallback if weird name
            
    if file_mapping:
        selected_file_display = st.sidebar.selectbox("Pilih Data Sebelumnya:", options=list(file_mapping.keys()))
        if st.sidebar.button("Muat Data Terpilih 📥", use_container_width=True):
            selected_file_path = file_mapping[selected_file_display]
            try:
                loaded_df = pd.read_csv(selected_file_path)
                st.session_state['raw_df'] = loaded_df
                st.session_state['processed_df'] = None
                st.session_state['ai_correction_metrics'] = None
                
                # Update session state based on filename
                parts = selected_file_path.replace("playstore_reviews_", "").replace(".csv", "").rsplit("_", 1)
                if len(parts) == 2:
                    st.session_state['app_id'] = parts[0].replace("_", ".")
                    try:
                        st.session_state['start_year'] = int(parts[1])
                    except ValueError:
                        pass
                
                st.sidebar.success(f"Berhasil memuat {len(loaded_df):,} review dari `{selected_file_path}`!")
            except Exception as e:
                st.sidebar.error(f"Gagal memuat file: {e}")
else:
    st.sidebar.info("Belum ada data historis yang tersimpan lokal.")

# UI Logic: IF raw data exists but hasn't been processed
if st.session_state['raw_df'] is not None and st.session_state.get('processed_df_temp') is None:
    st.info("✅ Data mentah berhasil diambil. Silakan periksa cuplikan di bawah, lalu proses sentimennya.")
    raw_df = st.session_state['raw_df']
    
    st.markdown("---")
    st.write("### 📊 Ringkasan Data Scraping")
    
    # Calculate counts for each score
    score_counts = raw_df['score'].value_counts()
    
    # Display metrics in 6 columns
    m_cols = st.columns(6)
    with m_cols[0]:
        st.metric("Total Review", f"{len(raw_df):,}")
    for i in range(5, 0, -1):
        with m_cols[6-i]:
            count = score_counts.get(i, 0)
            st.metric(f"Rating {i} ⭐", f"{count:,}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.write("### Cuplikan Data Mentah")
    # Using st.table for natural HTML text-wrapping and perfect column width distribution
    preview_df = raw_df[['userName', 'score', 'at', 'content']].head(10).copy()
    preview_df['score'] = preview_df['score'].astype(str) + " ⭐"
    preview_df.set_index('userName', inplace=True)
    st.table(preview_df)
    
    st.write("### Aksi")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        # Download button for raw CSV
        csv_data = raw_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Seluruh Data Mentah (CSV)",
            data=csv_data,
            file_name=f"raw_reviews_{st.session_state['app_id']}_{st.session_state['start_year']}.csv",
            mime='text/csv',
            use_container_width=True
        )
        
    with col_btn2:
        # Process button
        if st.button("2. Proses Analisis Sentimen & NLP ▶️", type="primary", use_container_width=True):
            with st.spinner("Menganalisis sentimen dan membersihkan teks..."):
                processed_df = preprocess_dataframe(raw_df)
                # Parse datetime if needed
                if not pd.api.types.is_datetime64_any_dtype(processed_df['at']):
                    processed_df['at'] = pd.to_datetime(processed_df['at'])
                
                st.session_state['processed_df'] = processed_df
                st.session_state['ai_correction_metrics'] = None
                st.rerun()

# UI Logic: IF processed data exists, show the full dashboard
if st.session_state['processed_df'] is not None:
    df = st.session_state['processed_df']
    
    st.markdown(f"**Aplikasi:** `{st.session_state['app_id']}` | **Tahun Filter Awal:** `{st.session_state['start_year']}`")
    st.success("✅ Dashboard siap digunakan! Gunakan filter di sebelah kiri untuk eksplorasi spesifik.")
    
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filter Dashboard")
    
    # Sentiment Filter
    sentiment_filter = st.sidebar.multiselect(
        "Pilih Sentimen:",
        options=df['sentiment'].unique(),
        default=df['sentiment'].unique()
    )
    
    # Rating Filter
    score_filter = st.sidebar.slider(
        "Pilih Rating (Bintang):",
        min_value=int(df['score'].min()),
        max_value=int(df['score'].max()),
        value=(int(df['score'].min()), int(df['score'].max()))
    )
    
    # Date Filter
    min_date = df['at'].min().date()
    max_date = df['at'].max().date()
    date_filter = st.sidebar.date_input(
        "Rentang Waktu Ulasan:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Apply Filters
    filtered_df = df[
        (df['sentiment'].isin(sentiment_filter)) &
        (df['score'] >= score_filter[0]) & 
        (df['score'] <= score_filter[1])
    ]
    
    if len(date_filter) == 2:
        start_dt, end_dt = date_filter
        filtered_df = filtered_df[
            (filtered_df['at'].dt.date >= start_dt) & 
            (filtered_df['at'].dt.date <= end_dt)
        ]

    # Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Review Terfilter", f"{len(filtered_df):,}")
    with col2:
        st.metric("Rata-rata Rating", f"{filtered_df['score'].mean():.2f} ⭐")
    with col3:
        positive_count = len(filtered_df[filtered_df['sentiment'] == 'Positive'])
        st.metric("Review Positif", f"{positive_count:,}")
    with col4:
        neutral_count = len(filtered_df[filtered_df['sentiment'] == 'Neutral'])
        st.metric("Review Netral", f"{neutral_count:,}")
    with col5:
        negative_count = len(filtered_df[filtered_df['sentiment'] == 'Negative'])
        st.metric("Review Negatif", f"{negative_count:,}")
        
    st.markdown("---")
    
    # Charts Row
    st.subheader("Visualisasi Sentimen & Kata Kunci")
    chart_col1, chart_col2 = st.columns([1, 2])
    
    with chart_col1:
        st.write("### Distribusi Sentimen")
        sentiment_counts = filtered_df['sentiment'].value_counts()
        
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = {'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#f1c40f'}
        pie_colors = [colors.get(x, '#bdc3c7') for x in sentiment_counts.index]
        
        if len(sentiment_counts) > 0:
            ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', 
                   startangle=90, colors=pie_colors, textprops={'fontsize': 12})
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.warning("Tidak ada data untuk pie chart.")
        
    with chart_col2:
        st.write("### Tren Sentimen Mingguan")
        
        # Group by week (start on Monday) and sentiment
        weekly_start = filtered_df['at'] - pd.to_timedelta(filtered_df['at'].dt.dayofweek, unit='d')
        weekly_sentiment = filtered_df.groupby([weekly_start.dt.date, 'sentiment']).size().unstack(fill_value=0)
        
        # Ensure all sentiment columns exist for the chart even if data is 0
        for sent in ['Positive', 'Negative', 'Neutral']:
            if sent not in weekly_sentiment.columns:
                weekly_sentiment[sent] = 0
                
        # Reorder columns for consistent coloring
        weekly_sentiment = weekly_sentiment[['Positive', 'Negative', 'Neutral']]
        
        # Plot using Streamlit's native bar chart (grouped, not stacked)
        st.bar_chart(weekly_sentiment, color=["#2ecc71", "#e74c3c", "#f1c40f"], stack=False)
        
    st.markdown("---")
    
    st.subheader("Visualisasi Kata Kunci (Word Cloud)")
    # Create tabs for each sentiment full width
    tabs = st.tabs(["🌐 Semua", "✅ Positif", "❌ Negatif", "😐 Netral"])
    
    sentiment_configs = [
        ("All", tabs[0], "viridis"),
        ("Positive", tabs[1], "Greens"),
        ("Negative", tabs[2], "Reds"),
        ("Neutral", tabs[3], "Blues")
    ]
    
    for sentiment_name, tab, cmap in sentiment_configs:
        with tab:
            if sentiment_name == "All":
                sentiment_df = filtered_df
            else:
                sentiment_df = filtered_df[filtered_df['sentiment'] == sentiment_name]
                
            text_for_wordcloud = " ".join(str(kw) for kw in sentiment_df['keywords'] if pd.notna(kw))
            
            if text_for_wordcloud.strip():
                wordcloud = WordCloud(width=1600, height=400, 
                                      background_color='white', 
                                      colormap=cmap,
                                      max_words=100).generate(text_for_wordcloud)
                
                fig, ax = plt.subplots(figsize=(15, 4))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info(f"Tidak cukup kata kunci untuk ditampilkan.")

    st.markdown("---")
    
    # Data Table
    st.subheader("Detail Ulasan dan Hasil Analisis Sentimen")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Menampilkan cuplikan 20 ulasan terbaru berdasarkan filter di atas:")
    with col2:
        csv_processed = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Seluruh Data Terfilter",
            data=csv_processed,
            file_name=f"analisis_review_{st.session_state['app_id']}.csv",
            mime='text/csv',
            use_container_width=True
        )
    
    # Using st.table for natural text wrapping
    display_cols = ['userName', 'score', 'sentiment', 'at', 'content']
    
    show_all = st.checkbox("Tampilkan Semua Data Terfilter", value=False)
    
    if show_all:
        preview_processed_df = filtered_df[display_cols].sort_values(by='at', ascending=False).copy()
    else:
        preview_processed_df = filtered_df[display_cols].sort_values(by='at', ascending=False).head(20).copy()
        
    preview_processed_df['score'] = preview_processed_df['score'].astype(str) + " ⭐"
    preview_processed_df.set_index('userName', inplace=True)
    st.table(preview_processed_df)
    
    st.markdown("---")
    st.header("🔍 Cek Anomali Lanjutan")
    st.write("Bagian ini mendeteksi ulasan dengan **kontradiksi** antara skor bintang Play Store dengan hasil deteksi algoritma teks dasar (Leksikon).")
    
    if st.session_state['ai_correction_metrics'] is not None:
        metrics = st.session_state['ai_correction_metrics']
        st.success(f"✨ **{metrics['total']}** ulasan anomali telah berhasil dianalisis ulang oleh AI (IndoBERT). Grafik di atas sudah memuat data terbaru.")
        st.write(f"**Hasil ({metrics['target_label']}):**")
        
        # Display breakdown columns based on results
        res_cols = st.columns(len(metrics['breakdown']))
        for idx, (sent, count) in enumerate(metrics['breakdown'].items()):
            with res_cols[idx]:
                st.metric(f"Menjadi {sent}", f"{count} review")
        st.write("---")
    
    # Create ai_verified column if it doesn't exist
    if 'ai_verified' not in df.columns:
        df['ai_verified'] = False
        
    # Calculate anomalies from the main df that haven't been verified by AI
    false_neg_mask = (df['score'] >= 4) & (df['sentiment'] == 'Negative') & (~df['ai_verified'])
    false_pos_mask = (df['score'] <= 2) & (df['sentiment'] == 'Positive') & (~df['ai_verified'])
    
    false_negatives = df[false_neg_mask]
    false_positives = df[false_pos_mask]
    
    has_anomalies = len(false_negatives) > 0 or len(false_positives) > 0
    
    if has_anomalies:
        st.warning(f"⚠️ Ditemukan **{len(false_negatives) + len(false_positives)}** ulasan dengan sentimen yang mencurigakan (Anomali).")
        st.write("Alih-alih membaca dan mengubah satu per satu, Anda dapat mendelegasikan AI canggih (IndoBERT) untuk memahami konteks kalimat sisa anomali ini secara mendalam.")
        
        st.write("---")
        col_anom1, col_anom2 = st.columns(2)
        
        with col_anom1:
            st.subheader("1. Anomali Bintang Tinggi (Rating 4 & 5)")
            st.metric("Total Data Mencurigakan (Bintang Tinggi namun teks terdeteksi Negatif)", f"{len(false_negatives)}")
            if len(false_negatives) > 0:
                st.write("**Contoh Data (Review Terbaik):**")
                st.dataframe(false_negatives[['userName', 'score', 'content']].head(3), hide_index=True, use_container_width=True)
                
                if st.button("✨ Koreksi Kategori Ini dengan IndoBERT", key="btn_ai_neg"):
                    with st.spinner("AI sedang membaca teliti konteks kalimat anomali Rating 4 & 5..."):
                        nlp = load_sentiment_pipeline()
                        texts = false_negatives['content'].tolist()
                        preds = classify_sentiment_indobert(texts, nlp)
                        for idx, p in zip(false_negatives.index, preds):
                            df.at[idx, 'sentiment'] = p
                            df.at[idx, 'ai_verified'] = True
                        
                        # Generate metrics
                        breakdown = pd.Series(preds).value_counts().to_dict()
                        st.session_state['ai_correction_metrics'] = {
                            'target_label': 'Anomali Bintang Tinggi (Semula Terdeteksi Negatif)',
                            'total': len(preds),
                            'breakdown': breakdown
                        }
                        
                        st.session_state['processed_df'] = df
                        st.rerun()

        with col_anom2:
            st.subheader("2. Anomali Bintang Rendah (Rating 1 & 2)")
            st.metric("Total Data Mencurigakan (Bintang Rendah namun teks terdeteksi Positif)", f"{len(false_positives)}")
            if len(false_positives) > 0:
                st.write("**Contoh Data (Review Terburuk):**")
                st.dataframe(false_positives[['userName', 'score', 'content']].head(3), hide_index=True, use_container_width=True)
                
                if st.button("✨ Koreksi Kategori Ini dengan IndoBERT", key="btn_ai_pos"):
                    with st.spinner("AI sedang membaca teliti konteks kalimat anomali Rating 1 & 2..."):
                        nlp = load_sentiment_pipeline()
                        texts = false_positives['content'].tolist()
                        preds = classify_sentiment_indobert(texts, nlp)
                        for idx, p in zip(false_positives.index, preds):
                            df.at[idx, 'sentiment'] = p
                            df.at[idx, 'ai_verified'] = True
                            
                        # Generate metrics
                        breakdown = pd.Series(preds).value_counts().to_dict()
                        st.session_state['ai_correction_metrics'] = {
                            'target_label': 'Anomali Bintang Rendah (Semula Terdeteksi Positif)',
                            'total': len(preds),
                            'breakdown': breakdown
                        }
                        
                        st.session_state['processed_df'] = df
                        st.rerun()
                        
    else:
        st.success("Hore! Saat ini status data sudah bersih dan selaras. Tidak ada kontradiksi anomali yang terdeteksi.")
        
    # Only show final results if AI has corrected something OR if there were no anomalies to begin with
    if st.session_state['ai_correction_metrics'] is not None or not has_anomalies:
        st.markdown("---")
        st.subheader("📈 Hasil Akhir Sentimen (Pasca Koreksi AI)")
        st.write("Distribusi akhir dari seluruh data review setelah melalui proses penyaringan Leksikon dasar dan verifikasi mendalam oleh IndoBERT.")
        
        final_sentiment_counts = df['sentiment'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = {'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#f1c40f'}
        pie_colors = [colors.get(x, '#bdc3c7') for x in final_sentiment_counts.index]
        
        if len(final_sentiment_counts) > 0:
            ax.pie(final_sentiment_counts, labels=final_sentiment_counts.index, autopct='%1.1f%%', 
                   startangle=90, colors=pie_colors, textprops={'fontsize': 12})
            ax.axis('equal')
            # Center the chart
            col_chart_1, col_chart_2, col_chart_3 = st.columns([1, 2, 1])
            with col_chart_2:
                st.pyplot(fig)
                
            st.write("---")
            st.write("### 🔍 Inspeksi Hasil Akhir Sentimen")
            st.write("Klik kategori di bawah ini untuk melihat daftar ulasannya:")
            
            # Create expanders for each sentiment category
            for sentiment_type in ['Positive', 'Negative', 'Neutral']:
                sentiment_data = df[df['sentiment'] == sentiment_type]
                if not sentiment_data.empty:
                    icon = "✅" if sentiment_type == 'Positive' else ("❌" if sentiment_type == 'Negative' else "😐")
                    with st.expander(f"{icon} Lihat Detail Ulasan {sentiment_type} ({len(sentiment_data)} data)"):
                        display_cols = ['userName', 'score', 'at', 'content']
                        preview_df = sentiment_data[display_cols].sort_values(by='at', ascending=False).copy()
                        preview_df['score'] = preview_df['score'].astype(str) + " ⭐"
                        preview_df.set_index('userName', inplace=True)
                        st.table(preview_df)
        else:
            st.info("Belum ada data sentimen yang cukup untuk ditampilkan.")
