# Membuktikan Sebab-Akibat dalam Kesehatan: Estimasi Efek Kausal Right Heart Catheterization (RHC) Terhadap Mortalitas ICU

Analisis statistik observational biostatistik untuk membuktikan hubungan sebab-akibat dari pemasangan Right Heart Catheterization (RHC) di ICU menggunakan kerangka statistik formal: Causal Directed Acyclic Graph (DAG), Propensity Score Matching (PSM), Inverse Probability Weighting (IPW), dan Doubly Robust (AIPW) Estimation.

---

## 🎯 Pertanyaan Kausal
> **"Apakah pemasangan Right Heart Catheterization (RHC) pada pasien ICU meningkatkan risiko mortalitas 30 hari?"**

Studi kasus ini mereplikasi penelitian SUPPORT klasik (Connors et al., 1996). Analisis naif awal menunjukkan korelasi bahwa RHC tampak membahayakan (+5.07% mortalitas). Namun, ini karena *confounding by indication*—pasien yang dipasang RHC memang secara klinis jauh lebih sakit saat masuk ICU. Proyek ini membuktikan efek kausal sebenarnya setelah menghilangkan bias seleksi tersebut secara statistik.

---

## 🗺️ Causal Directed Acyclic Graph (DAG)
Kami memodelkan hubungan sebab-akibat secara eksplisit menggunakan DAG untuk mengidentifikasi jalur belakang (*backdoor path*):

![Causal DAG](reports/figures/04_causal_dag.png)

- **Treatment (T):** Pemasangan RHC (`treatment`).
- **Outcome (Y):** Mortalitas 30 Hari (`outcome`).
- **Mediator (M):** Perubahan tatalaksana klinis setelah RHC terpasang. Karena kita ingin mengukur **efek kausal total**, mediator M **tidak disesuaikan** (tidak dikontrol).
- **Confounders (X):** 68 variabel klinis (skor keparahan APACHE III, status hemodinamika, vital signs, komorbiditas, usia, dll).
- **Jalur Belakang (Backdoor):** `T <-- X --> Y`. Jalur ini ditutup secara valid dengan mengontrol ke-68 confounder.

---

## 📈 Ringkasan Hasil Estimasi Efek Kausal

Setelah menyeimbangkan karakteristik klinis antara kelompok RHC dan Kontrol, bias korelasi naif berhasil dikoreksi. Di bawah ini adalah perbandingan hasil efek (Risk Difference):

| Metode | ATE (95% CI) | ATT (95% CI) | Keterangan |
| --- | --- | --- | --- |
| **Naif (Korelasi)** | +5.07% (+3.76%, +6.38%) | +5.07% (+3.76%, +6.38%) | Mengabaikan seluruh bias seleksi |
| **PSM (1:1 Matching)** | - | **+3.48% (+1.10%, +5.86%)** | Pencocokan karakteristik klinis 1:1 |
| **IPW (Weighting)** | **+3.10% (+1.16%, +5.04%)** | **+2.73% (+0.78%, +4.68%)** | Pembobotan peluang terbalik stabil |
| **Doubly Robust (AIPW)** | **+2.95% (+1.04%, +4.86%)** | **+3.94% (+1.92%, +5.96%)** | Kombinasi model treatment & outcome |

*Confidence Intervals (CI) 95% dihitung menggunakan bootstrap (100 resamples).*

### Temuan Utama:
1. **Bias Korelasi Naif Terkoreksi:** Asosiasi naif (+5.07%) terbukti bias ke atas karena faktor keparahan klinis awal pasien RHC yang tinggi.
2. **Efek Kausal Signifikan:** Setelah menyelaraskan 68 confounder, efek kausal RHC terhadap peningkatan mortalitas 30 hari adalah sekitar **+2.73% hingga +3.94%** (tetap meningkatkan kematian secara signifikan).
3. **Konfirmasi Klinis:** Hasil ini mereplikasi temuan SUPPORT Study (1996) bahwa tindakan diagnostik invasif RHC secara kausal merugikan pasien ICU dan meningkatkan mortalitas 30 hari sebesar ~3%.

---

## 🛡️ Uji Refutasi DoWhy & Sensitivitas E-value
Kredibilitas model kausal divalidasi dengan stress-testing DoWhy:

1. **Placebo Treatment Test:** Efek kausal awal runtuh menjadi **-2.33%** (p-value = 0.16) ketika RHC diganti dengan random noise. Lolos (tidak mendeteksi hubungan semu).
2. **Random Common Cause Test:** Efek kausal tetap stabil di angka **+3.99%** (p-value = 1.00) setelah variabel confounder acak ditambahkan. Lolos.
3. **Data Subset Test:** Efek kausal tetap konsisten di angka **+3.87%** (p-value = 0.90) pada 80% subset acak data. Lolos.
4. **Analisis Sensitivitas E-value:** Diperoleh **E-value = 1.32**. Sangat tidak mungkin ada confounder tersembunyi yang belum diselaraskan yang memiliki kekuatan Risk Ratio sebesar 1.32 terhadap keputusan tindakan RHC dan mortalitas secara bersamaan. Temuan kausal ini terbukti **sangat kokoh**.

---

## ⚙️ Cara Menjalankan Kode

### 1. Prasyarat (Requirements)
Pastikan Python 3.12+ sudah terpasang.

### 2. Kloning & Pengaturan Lingkungan Virtual (Virtual Env)
```bash
# Buat & aktifkan virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Pasang dependensi
pip install -r requirements.txt
```
*(Catatan: Jika Anda di Windows dan mengalami error DLL statsmodels karena pembatasan panjang path, buatlah folder venv di direktori dengan path yang lebih pendek seperti C:\venv atau di app data).*

### 3. Eksekusi Script Pipeline
Anda dapat menjalankan script secara terpisah dari folder root proyek:
```bash
# 1. Unduh dan preprocess RHC dataset
python src/data_loader.py

# 2. Jalankan EDA & Covariate Balance unadjusted
python src/eda.py

# 3. Jalankan Causal DAG & Identifikasi DoWhy
python src/dag.py

# 4. Jalankan Estimasi Efek Kausal (PSM, IPW, DR) & Bootstrap
python src/estimators.py

# 5. Jalankan Evaluasi & Render Grafik Estimasi
python src/generate_estimation_plots.py

# 6. Jalankan Uji Refutasi DoWhy & Sensitivitas E-value
python src/refute.py
```

### 4. Menjalankan Jupyter Notebooks
Seluruh fase di atas didokumentasikan dalam format notebook interaktif yang tersimpan di folder `notebooks/`:
- `notebooks/01_eda.ipynb` (Eksplorasi Data awal & balance unadjusted)
- `notebooks/02_dag_identification.ipynb` (Causal DAG & identifikasi Backdoor)
- `notebooks/03_estimation.ipynb` (Estimasi efek PSM, IPW, AIPW & overlap)
- `notebooks/04_refutation.ipynb` (Uji refutasi DoWhy & E-value)

### 5. Menjalankan Dashboard Interaktif Streamlit
Visualisasikan temuan secara interaktif via web browser:
```bash
streamlit run app.py
```

---

## ⚠️ Disclaimer
Analisis ini dirancang khusus untuk tujuan edukatif dan demonstrasi portfolio sains data/biostatistika. Hasil analisis menggunakan data SUPPORT Study historis tahun 1996 dan tidak boleh dijadikan acuan medis klinis praktis pada saat ini.