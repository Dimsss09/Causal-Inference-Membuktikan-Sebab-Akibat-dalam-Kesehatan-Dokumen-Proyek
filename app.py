import streamlit as st
import pandas as pd
import numpy as np
import os
import base64

# Set page config for premium look
st.set_page_config(
    page_title="RHC Causal Inference Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Project root path resolution
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Helper function to load image to base64
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None

# Custom CSS for modern premium styling (Industry Standard)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Apply Font Globally */
    .stApp, .main-title, .subtitle, .metric-card, .explanation-box, p, span, div, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* App Body Background with subtle medical theme radial gradients */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 80% 20%, rgba(52, 152, 219, 0.1) 0%, rgba(255, 255, 255, 0) 50%),
                    radial-gradient(circle at 20% 80%, rgba(26, 188, 156, 0.08) 0%, rgba(255, 255, 255, 0) 50%),
                    linear-gradient(135deg, #f4f7f6 0%, #ffffff 100%) !important;
    }
    
    /* Force Dark Slate text color inside Main Container to prevent white text on light background */
    [data-testid="stAppViewContainer"] p, 
    [data-testid="stAppViewContainer"] span:not(.main-title):not(.subtitle), 
    [data-testid="stAppViewContainer"] label, 
    [data-testid="stAppViewContainer"] li,
    [data-testid="stAppViewContainer"] h1:not(.main-title), 
    [data-testid="stAppViewContainer"] h2, 
    [data-testid="stAppViewContainer"] h3, 
    [data-testid="stAppViewContainer"] h4, 
    [data-testid="stAppViewContainer"] h5, 
    [data-testid="stAppViewContainer"] h6 {
        color: #1e293b !important;
    }
    
    /* Style inline code elements for better contrast */
    [data-testid="stAppViewContainer"] code {
        color: #e11d48 !important;
        background-color: #f1f5f9 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: monospace !important;
    }
    
    /* Sidebar Styling - Modern dark slate gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #eceff1 !important;
    }
    
    /* Custom radio buttons in sidebar */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin-bottom: 10px !important;
        transition: all 0.25s ease-in-out !important;
        cursor: pointer;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.12) !important;
        border-color: #1abc9c !important;
        transform: translateX(4px);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, #1abc9c 0%, #16a085 100%) !important;
        border-color: #1abc9c !important;
        box-shadow: 0 4px 10px rgba(26, 188, 156, 0.3);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] * {
        color: #ffffff !important;
    }
    
    /* Main Titles */
    .main-title {
        font-size: 38px;
        font-weight: 800;
        background: linear-gradient(135deg, #2c3e50 0%, #2980b9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }
    .subtitle {
        font-size: 18px;
        color: #64748b !important;
        margin-bottom: 25px;
        font-weight: 400;
    }
    
    /* Premium Metric Cards with Hover Animation */
    .metric-card {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px !important;
        padding: 20px 22px !important;
        border: 1px solid rgba(224, 231, 238, 0.9) !important;
        border-left: 6px solid #2980b9;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 15px;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08) !important;
        border-color: rgba(41, 128, 185, 0.4) !important;
    }
    .metric-title {
        font-size: 13px;
        color: #64748b !important;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #0f172a !important;
        margin-top: 4px;
    }
    .metric-delta {
        font-size: 13px;
        font-weight: bold;
        margin-top: 6px;
    }
    
    /* Educational Info Box */
    .explanation-box {
        background: rgba(235, 245, 251, 0.8) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px !important;
        padding: 20px 24px !important;
        border: 1px solid rgba(174, 214, 241, 0.7) !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.01) !important;
        margin-bottom: 20px;
    }
    .explanation-box h4 {
        color: #2980b9 !important;
        font-weight: 700;
        font-size: 18px;
        margin-bottom: 12px;
        margin-top: 0;
    }
    .explanation-box ul {
        margin: 0;
        padding-left: 20px;
    }
    .explanation-box li {
        margin-bottom: 8px;
        color: #334155 !important;
        line-height: 1.5;
    }
    .explanation-box li:last-child {
        margin-bottom: 0;
    }
    
    /* Logo Pulsing Animation */
    .logo-img {
        animation: logoPulse 4s infinite ease-in-out;
        transition: all 0.3s ease;
    }
    .logo-img:hover {
        transform: rotate(5deg) scale(1.05);
    }
    @keyframes logoPulse {
        0% { transform: scale(1); filter: drop-shadow(0 2px 5px rgba(26, 188, 156, 0.15)); }
        50% { transform: scale(1.03); filter: drop-shadow(0 8px 20px rgba(26, 188, 156, 0.4)); }
        100% { transform: scale(1); filter: drop-shadow(0 2px 5px rgba(26, 188, 156, 0.15)); }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Logo and Title
logo_img_path = os.path.join(PROJECT_ROOT, "reports", "figures", "medical_causal_logo.png")
logo_base64 = get_image_base64(logo_img_path)

if logo_base64:
    st.sidebar.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px; flex-direction: column; padding-top: 10px;">
            <img class="logo-img" src="data:image/png;base64,{logo_base64}" style="width: 110px; height: 110px; border-radius: 50%; border: 3px solid #1abc9c; object-fit: cover; background-color: white;" />
            <h2 style="color: white; margin-top: 12px; font-size: 20px; font-weight: 700; text-align: center; font-family: 'Outfit', sans-serif;">RHC Causal Lab</h2>
        </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("# 🏥 RHC Causal Lab")

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigasi Halaman:",
    ["Ringkasan Proyek", "1. Eksplorasi Data & Imbalance", "2. Pemodelan Kausal & DAG", "3. Estimasi Efek & Overlap", "4. Uji Refutasi & Sensitivitas"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Catatan Edukatif:**\n"
    "Proyek ini bertujuan membuktikan sebab-akibat dari data observasional ICU (SUPPORT Study, 1996)."
)

# Load data if available
@st.cache_data
def load_summary_data():
    csv_path = os.path.join(PROJECT_ROOT, "data", "processed", "causal_estimates_summary.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

summary_df = load_summary_data()

# Render pages based on selection
if page == "Ringkasan Proyek":
    st.markdown('<div class="main-title">Membuktikan Sebab-Akibat dalam Kesehatan</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Estimasi Efek Kausal Right Heart Catheterization (RHC) Terhadap Mortalitas ICU</div>', unsafe_allow_html=True)
    
    # Overview metrics grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            '<div class="metric-card" style="border-left-color: #34495e;">'
            '<div class="metric-title">Total Pasien ICU</div>'
            '<div class="metric-value">5,735</div>'
            '<div class="metric-delta" style="color: #7f8c8d;">Data Observational SUPPORT</div>'
            '</div>', unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '<div class="metric-card" style="border-left-color: #e74c3c;">'
            '<div class="metric-title">Mortalitas RHC (Treated)</div>'
            '<div class="metric-value">68.04%</div>'
            '<div class="metric-delta" style="color: #e74c3c;">2,184 Pasien</div>'
            '</div>', unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            '<div class="metric-card" style="border-left-color: #2ecc71;">'
            '<div class="metric-title">Mortalitas Kontrol (No RHC)</div>'
            '<div class="metric-value">62.97%</div>'
            '<div class="metric-delta" style="color: #2ecc71;">3,551 Pasien</div>'
            '</div>', unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            '<div class="metric-card" style="border-left-color: #f39c12;">'
            '<div class="metric-title">Selisih Naif (Bias)</div>'
            '<div class="metric-value">+5.07%</div>'
            '<div class="metric-delta" style="color: #e74c3c;">RHC tampak membahayakan</div>'
            '</div>', unsafe_allow_html=True
        )
        
    st.markdown("### Latar Belakang Klinis")
    st.write(
        "Kebanyakan analisis data sains berhenti di korelasi. Namun, di bidang kesehatan, pertanyaan terpenting bersifat **kausal**: "
        "*\"Apakah pemasangan Right Heart Catheterization (RHC) benar-benar MENYEBABKAN kenaikan risiko kematian, atau hanya kebetulan?\"* "
        "Pasien yang dipasang alat RHC (kateterisasi jantung kanan) di ICU umumnya memang berada dalam kondisi klinis yang lebih kritis (*confounding by indication*). "
        "Oleh karena itu, perbandingan naif langsung antara kelompok RHC dan kontrol akan memicu bias yang sangat menyesatkan."
    )
    
    st.markdown("### Mengapa Causal Inference?")
    st.write(
        "Dengan menggunakan kerangka statistik formal (DAG, Propensity Score, IPW, dan Doubly Robust), kita dapat menyelaraskan "
        "dan menyeimbangkan karakteristik klinis antara pasien RHC dan kontrol. Ini seolah-olah menciptakan uji klinis acak (RCT) "
        "tiruan dari data observasional, sehingga kita bisa mengukur efek kausal yang sebenarnya secara objektif."
    )
    
    st.markdown("### Alur Pengerjaan (Roadmap)")
    st.markdown(
        "- **Fase 0 & 1:** Setup lingkungan proyek & Eksplorasi Data awal (EDA).\n"
        "- **Fase 2:** Pemodelan hubungan kausal secara eksplisit menggunakan Causal DAG.\n"
        "- **Fase 3:** Estimasi efek kausal menggunakan metode Propensity Score Matching (PSM), IPW, dan Doubly Robust.\n"
        "- **Fase 4:** Validasi model kausal melalui uji refutasi DoWhy (placebo treatment, random common cause, data subset) dan analisis sensitivitas E-value."
    )

elif page == "1. Eksplorasi Data & Imbalance":
    st.header("1. Eksplorasi Data & Evaluasi Ketidakseimbangan Awal")
    st.write(
        "Pada tahap awal, kita melihat bagaimana distribusi pasien ICU yang menerima tindakan RHC serta membandingkannya dengan "
        "tingkat mortalitas naif di kedua kelompok. Terpenting, kita mengevaluasi Standardized Mean Difference (SMD) dari kovariat "
        "awal untuk mengukur bias seleksi."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribusi Tindakan RHC")
        img_path = os.path.join(PROJECT_ROOT, "reports", "figures", "01_treatment_distribution.png")
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.warning("Grafik distribusi treatment belum dibuat. Jalankan eda.py.")
            
    with col2:
        st.subheader("Tingkat Mortalitas Naif")
        img_path2 = os.path.join(PROJECT_ROOT, "reports", "figures", "02_outcome_by_treatment.png")
        if os.path.exists(img_path2):
            st.image(img_path2, use_container_width=True)
        else:
            st.warning("Grafik tingkat mortalitas naif belum dibuat.")

    st.markdown("---")
    st.subheader("Love Plot: Evaluasi Ketidakseimbangan Kovariat Awal (Sebelum Penyesuaian)")
    st.write(
        "Nilai Standardized Mean Difference (SMD) di atas **0.1** menunjukkan ketidakseimbangan kovariat yang parah. "
        "Di bawah ini adalah 35 variabel teratas yang memiliki ketidakseimbangan paling menonjol sebelum disesuaikan."
    )
    
    img_path3 = os.path.join(PROJECT_ROOT, "reports", "figures", "03_love_plot_unadjusted.png")
    if os.path.exists(img_path3):
        st.image(img_path3, use_container_width=False, width=800)
    else:
        st.warning("Love Plot unadjusted belum dibuat. Jalankan eda.py.")
        
    st.markdown(
        "<div class='explanation-box'>"
        "<h4>Temuan Imbalance:</h4>"
        "<ul>"
        "<li>Ditemukan <b>42 dari 68 kovariat</b> memiliki SMD > 0.1, menandakan bias seleksi yang parah.</li>"
        "<li>Variabel keparahan klinis seperti skor APACHE III (<code>aps1</code>, SMD = +0.50) dan hemodinamika seperti "
        "tekanan darah rata-rata (<code>meanbp1</code>, SMD = -0.45) menunjukkan ketimpangan yang sangat signifikan.</li>"
        "<li><b>Kesimpulan:</b> Pasien RHC secara sistematis jauh lebih sakit. Membandingkan mortalitas secara naif "
        "sangat tidak valid karena bias indikasi medis ini.</li>"
        "</ul>"
        "</div>", unsafe_allow_html=True
    )

    st.markdown("---")
    st.subheader("Tabel Karakteristik Klinis Pasien (Table 1) - Pre vs Post Matching")
    st.write(
        "Di bawah ini adalah Tabel Karakteristik Klinis (Table 1) standar jurnal medis. Tabel ini membandingkan "
        "distribusi demografi, status fisiologis (keparahan penyakit), komorbiditas, dan diagnosis masuk "
        "antara kelompok RHC dan Kontrol. Terlihat bahwa setelah pencocokan (Matched), perbedaan (SMD) di semua "
        "variabel klinis utama turun drastis hingga mendekati 0.00."
    )
    
    table1_path = os.path.join(PROJECT_ROOT, "data", "processed", "table1.csv")
    if os.path.exists(table1_path):
        table1_df = pd.read_csv(table1_path)
        st.dataframe(table1_df, hide_index=True, use_container_width=True)
    else:
        st.warning("Tabel karakteristik klinis (Table 1) tidak ditemukan. Jalankan generate_table1.py.")

elif page == "2. Pemodelan Kausal & DAG":
    st.header("2. Pemodelan Kausal (Directed Acyclic Graph - DAG)")
    st.write(
        "Untuk mengidentifikasi hubungan sebab-akibat secara benar, kita harus memetakan asumsi kausal secara eksplisit "
        "dalam bentuk Directed Acyclic Graph (DAG) guna menentukan set penyesuaian (*adjustment set*) backdoor yang valid."
    )
    
    img_path4 = os.path.join(PROJECT_ROOT, "reports", "figures", "04_causal_dag.png")
    if os.path.exists(img_path4):
        st.image(img_path4, use_container_width=False, width=800)
    else:
        st.warning("Visualisasi DAG belum dibuat. Jalankan plot_dag().")
        
    st.markdown(
        "<div class='explanation-box'>"
        "<h4>Struktur DAG & Identifikasi:</h4>"
        "<ul>"
        "<li><b>Treatment (T):</b> Pemasangan Right Heart Catheterization (RHC).</li>"
        "<li><b>Outcome (Y):</b> Mortalitas 30 Hari.</li>"
        "<li><b>Confounders (X):</b> 68 variabel klinis (APACHE, hemodinamika, komorbiditas, usia, jenis kelamin, dll).</li>"
        "<li><b>Jalur Belakang (Backdoor Path):</b> Jalur <code>T <-- X --> Y</code> menyebabkan bias seleksi. Kita wajib menutup "
        "jalur ini dengan menyesuaikan X.</li>"
        "<li><b>Mediator (M):</b> Perubahan tatalaksana klinis setelah RHC terpasang. Karena kita tertarik pada <b>efek kausal total</b> "
        "RHC terhadap mortalitas, mediator M <b>tidak boleh disesuaikan</b> (menyesuaikannya justru memicu bias mediator).</li>"
        "<li><b>Hasil Identifikasi:</b> Kriteria backdoor teridentifikasi secara valid dengan menutup 68 confounder.</li>"
        "</ul>"
        "</div>", unsafe_allow_html=True
    )

elif page == "3. Estimasi Efek & Overlap":
    st.header("3. Estimasi Efek Kausal & Evaluasi Keseimbangan Akhir")
    st.write(
        "Di bawah ini adalah perbandingan hasil estimasi efek kausal ATE (Average Treatment Effect) dan "
        "ATT (Average Treatment Effect on the Treated) beserta evaluasi asumsi overlap dan keseimbangan kovariat akhir."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Evaluasi Asumsi Overlap (Positivity)")
        st.write("Mengecek kecocokan (*common support*) distribusi Propensity Score kelompok RHC vs Kontrol.")
        img_path5 = os.path.join(PROJECT_ROOT, "reports", "figures", "05_propensity_score_overlap.png")
        if os.path.exists(img_path5):
            st.image(img_path5, use_container_width=True)
        else:
            st.warning("Overlap plot belum dibuat.")
            
    with col2:
        st.subheader("Perbandingan Keseimbangan Kovariat (Love Plot)")
        st.write("Membandingkan SMD sebelum (Unadjusted) vs sesudah penyesuaian (Matching 1:1).")
        img_path6 = os.path.join(PROJECT_ROOT, "reports", "figures", "06_love_plot_comparison.png")
        if os.path.exists(img_path6):
            st.image(img_path6, use_container_width=True)
        else:
            st.warning("Perbandingan Love Plot belum dibuat.")
            
    st.markdown("---")
    st.subheader("Perbandingan Efek Estimasi (Point Estimate & 95% Bootstrap CI)")
    
    col_plot, col_tab = st.columns([1.2, 1.0])
    with col_plot:
        img_path7 = os.path.join(PROJECT_ROOT, "reports", "figures", "07_effect_comparison.png")
        if os.path.exists(img_path7):
            st.image(img_path7, use_container_width=True)
        else:
            st.warning("Causal effect comparison plot belum dibuat. Jalankan estimators.py.")
            
    with col_tab:
        st.markdown("**Tabel Hasil Estimasi:**")
        if summary_df is not None:
            # Format float columns
            formatted_df = summary_df.copy()
            for col in ['ATE', 'ATE_CI_Lower', 'ATE_CI_Upper', 'ATT', 'ATT_CI_Lower', 'ATT_CI_Upper']:
                formatted_df[col] = formatted_df[col].apply(lambda x: f"{x*100:+.2f}%" if pd.notnull(x) else "-")
            st.dataframe(formatted_df, hide_index=True)
        else:
            st.warning("Data ringkasan estimasi tidak ditemukan.")
            
    st.markdown(
        "<div class='explanation-box'>"
        "<h4>Interpretasi Hasil Estimasi:</h4>"
        "<ul>"
        "<li><b>Positivity Terpenuhi:</b> KDE overlap menunjukkan dukungan bersama yang sangat baik di seluruh rentang propensity score.</li>"
        "<li><b>Balancing Sempurna:</b> Setelah Propensity Score Matching (1:1), jumlah variabel yang tidak seimbang (|SMD| > 0.1) berkurang dari <b>42 variabel menjadi 0 variabel</b>. Bias seleksi berhasil dihilangkan.</li>"
        "<li><b>Koreksi Efek:</b> Perbedaan mortalitas naif (+5.07%) terbukti bias ke atas. Setelah penyesuaian kausal, efek kausal "
        "pemasangan RHC berkisar antara <b>+2.73% hingga +3.94%</b> (tetap meningkatkan risiko kematian).</li>"
        "<li><b>Interpretasi Klinis:</b> Hasil ini membuktikan secara ilmiah bahwa pemasangan RHC pada pasien ICU "
        "tidak memberikan manfaat kelangsungan hidup dan justru secara kausal meningkatkan mortalitas 30 hari sebesar ~3% (sesuai studi SUPPORT 1996).</li>"
        "</ul>"
        "</div>", unsafe_allow_html=True
    )

elif page == "4. Uji Refutasi & Sensitivitas":
    st.markdown('<div class="main-title">4. Validasi Kausalitas & Analisis Sensitivitas</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Menguji Kredibilitas dan Ketahanan Hubungan Sebab-Akibat Terhadap Faktor Tersembunyi</div>', unsafe_allow_html=True)
    
    # Tabs for industry standard organization
    tab1, tab2, tab3 = st.tabs([
        "🛡️ Uji Refutasi (Stress Testing)", 
        "📊 Diagnostik Model & Kestabilan Bobot", 
        "🔮 Simulator Sensitivitas E-Value"
    ])
    
    with tab1:
        st.subheader("Uji Refutasi Formal (DoWhy Framework)")
        st.write(
            "Dalam analisis data observasional, pembuktian sebab-akibat harus lolos dari tantangan uji refutasi formal. "
            "Di bawah ini adalah 3 pengujian stress-testing untuk mengonfirmasi bahwa hubungan RHC dengan mortalitas "
            "bukanlah korelasi semu (*spurious association*)."
        )
        
        # Grid layout for 3 refuters
        col_ref1, col_ref2, col_ref3 = st.columns(3)
        with col_ref1:
            st.markdown(
                '<div class="metric-card" style="border-left-color: #e74c3c;">'
                '<div class="metric-title">Placebo Treatment</div>'
                '<div class="metric-value">-2.33%</div>'
                '<div class="metric-delta" style="color: #27ae60;">✔ Lolos Uji</div>'
                '<div style="font-size:12px; color:#64748b; margin-top:8px;">P-value: 0.16 (Tak Signifikan)</div>'
                '</div>', unsafe_allow_html=True
            )
            st.info(
                "**Placebo Test:** Mengganti tindakan RHC asli dengan noise acak. "
                "Efek kausal teramati (+3.99%) runtuh menjadi tidak signifikan (-2.33%), membuktikan model bebas dari hubungan palsu."
            )
            
        with col_ref2:
            st.markdown(
                '<div class="metric-card" style="border-left-color: #2ecc71;">'
                '<div class="metric-title">Random Common Cause</div>'
                '<div class="metric-value">+3.99%</div>'
                '<div class="metric-delta" style="color: #27ae60;">✔ Lolos Uji</div>'
                '<div style="font-size:12px; color:#64748b; margin-top:8px;">P-value: 1.00 (Efek Stabil)</div>'
                '</div>', unsafe_allow_html=True
            )
            st.info(
                "**Random Cause:** Memasukkan noise acak sebagai confounder tambahan. "
                "Estimasi efek kausal tetap stabil di angka +3.99%, membuktikan ketahanan estimator terhadap variansi noise luar."
            )
            
        with col_ref3:
            st.markdown(
                '<div class="metric-card" style="border-left-color: #3498db;">'
                '<div class="metric-title">Data Subset Refuter</div>'
                '<div class="metric-value">+3.87%</div>'
                '<div class="metric-delta" style="color: #27ae60;">✔ Lolos Uji</div>'
                '<div style="font-size:12px; color:#64748b; margin-top:8px;">P-value: 0.90 (Kekokohan Sampel)</div>'
                '</div>', unsafe_allow_html=True
            )
            st.info(
                "**Data Subset:** Mengestimasi efek ulang hanya pada 80% data acak. "
                "Efek kausal tetap konsisten (+3.87%), menunjukkan kestabilan tinggi terhadap fluktuasi data."
            )
            
    with tab2:
        st.subheader("Metrik Kinerja & Diagnostik Bobot Propensity Score")
        st.write(
            "Keabsahan estimasi IPW dan Doubly Robust bergantung sepenuhnya pada kualitas model propensity score. "
            "Berikut adalah evaluasi diagnostik model standar industri."
        )
        
        col_diag1, col_diag2 = st.columns(2)
        with col_diag1:
            st.markdown("#### 🔍 Kinerja Model Propensity Score (Logistic Regression)")
            st.markdown(
                '<div class="metric-card" style="border-left-color: #f39c12;">'
                '<div class="metric-title">Diskriminasi (AUC-ROC)</div>'
                '<div class="metric-value">0.824</div>'
                '<div style="font-size:12px; color:#64748b; margin-top:8px;">Menunjukkan bias seleksi awal yang sangat kuat</div>'
                '</div>', unsafe_allow_html=True
            )
            st.markdown(
                '<div class="metric-card" style="border-left-color: #9b59b6;">'
                '<div class="metric-title">Kalibrasi (Brier Score)</div>'
                '<div class="metric-value">0.187</div>'
                '<div style="font-size:12px; color:#64748b; margin-top:8px;">Probabilitas propensity score terkalibrasi baik</div>'
                '</div>', unsafe_allow_html=True
            )
            
        with col_diag2:
            st.markdown("#### ⚖️ Kestabilan Ukuran Sampel Efektif (ESS)")
            st.write(
                "IPW dapat mengalami ketidakstabilan variansi jika terdapat bobot ekstrem. "
                "ESS (Effective Sample Size) mengevaluasi seberapa stabil distribusi bobot:"
            )
            
            ess_data = {
                "Tahapan Skenario": ["Sebelum Penyesuaian (Raw)", "Setelah PSM (Matching 1:1)", "Setelah IPW (Weighting)"],
                "Treated ESS": [2184, 2184, 1940.6],
                "Control ESS": [3551, 2184, 3012.4],
                "Total ESS": [5735, 4368, 4953.0]
            }
            st.dataframe(pd.DataFrame(ess_data), hide_index=True, use_container_width=True)
            st.info(
                "**Interpretasi ESS:** Penurunan ESS yang relatif kecil pada IPW (dari 5,735 menjadi 4,953) "
                "membuktikan tidak adanya bobot ekstrem dominan (no extreme weights), sehingga variansi estimasi stabil."
            )
            
    with tab3:
        st.subheader("Analisis Sensitivitas VanderWeele E-Value")
        st.write(
            "Analisis ini mengukur ketahanan hasil temuan terhadap bias tersembunyi (*unobserved confounding*). "
            "Slider di bawah menyimulasikan kekuatan faktor tersembunyi tersebut terhadap peluang tindakan RHC dan tingkat kematian."
        )
        
        col_sens1, col_sens2 = st.columns([1, 1.2])
        with col_sens1:
            st.markdown(
                '<div class="metric-card" style="border-left-color: #9b59b6; background-color: #f5eef8;">'
                '<div class="metric-title">E-Value Terhitung</div>'
                '<div class="metric-value">1.32</div>'
                '<div class="metric-delta" style="color: #8e44ad;">Berdasarkan Causal Risk Ratio (RR) = 1.06</div>'
                '</div>', unsafe_allow_html=True
            )
            
            rr_unobs = st.slider(
                "Asumsi Kekuatan Confounder Tersembunyi (RR_u):",
                min_value=1.0,
                max_value=2.0,
                value=1.2,
                step=0.05,
                help="Kekuatan asosiasi independen dari variabel klinis tersembunyi terhadap RHC dan kematian."
            )
            
        with col_sens2:
            st.markdown("#### ⚙️ Hasil Simulasi Kekokohan Model")
            if rr_unobs < 1.32:
                st.success(
                    f"🟢 **Robust! (RR_u = {rr_unobs:.2f} < 1.32)**\n\n"
                    "Efek kausal pemasangan RHC **TETAP SIGNIFIKAN**. "
                    "Variabel tersembunyi dengan kekuatan bias sebesar ini tidak cukup kuat untuk mereduksi efek kematian RHC menjadi nol."
                )
            else:
                st.error(
                    f"🔴 **Sensitif! (RR_u = {rr_unobs:.2f} >= 1.32)**\n\n"
                    "Efek kausal **DAPAT TERJELASKAN (Nullified)**.\n\n"
                    "Bila terdapat variabel klinis tersembunyi yang belum dimasukkan model dengan kekuatan RR >= 1.32, "
                    "efek kausal yang kita amati bisa jadi merupakan bias seleksi."
                )
                
            st.markdown(
                "**Opini Kredibilitas Klinis:**\n"
                "Mengingat kita telah menyesuaikan **68 variabel klinis** (APACHE III, status gagal organ, vital signs, dll.), "
                "sangat kecil kemungkinan ada variabel tersembunyi lain yang memiliki kekuatan independen RR >= 1.32. "
                "Oleh karena itu, temuan kausal peningkatan mortalitas RHC dinilai **sangat kokoh**."
            )

    st.markdown("---")
    st.subheader("Kesimpulan Akhir & Disclaimer")
    st.warning(
        "**Disclaimer:** Analisis ini dikembangkan untuk tujuan edukatif dan portfolio biostatistik/data sains. "
        "Hasil ini mereplikasi studi historis SUPPORT (1996) dan tidak boleh dijadikan acuan keputusan klinis medis langsung pada saat ini."
    )
    st.success(
        "🎉 **Portfolio Causal Inference Sukses!** Proyek ini secara meyakinkan mendemonstrasikan bagaimana kerangka statistika formal "
        "mampu mengoreksi bias korelasi naif data observasional kesehatan untuk membuktikan efek sebab-akibat yang nyata dan kokoh."
    )

