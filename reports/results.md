# Ringkasan Analisis Causal Inference: RHC & Mortalitas ICU

## Hasil Exploratory Data Analysis (EDA) - Fase 1

- **Total Sampel:** 5735 pasien ICU.
  - **Kelompok Treatment (RHC):** 2184 pasien (38.08%).
  - **Kelompok Kontrol (No RHC):** 3551 pasien (61.92%).

### Perbandingan Naif (Korelasi Awal)
- **Tingkat Mortalitas 30 Hari - Kelompok RHC:** 68.04%
- **Tingkat Mortalitas 30 Hari - Kelompok Kontrol:** 62.97%
- **Perbedaan Efek Naif (Naive Risk Difference):** +5.07% (RHC tampak meningkatkan kematian)

> **Catatan:** Perbedaan naif ini sangat bias karena *confounding by indication*—pasien yang dipasang RHC umumnya berada dalam kondisi klinis yang lebih parah.

### Pemeriksaan Missing Values
Ditemukan beberapa nilai yang hilang di dataset:
- Kolom `cat2`: 4535 nilai kosong.
- Kolom `dschdte`: 1 nilai kosong.
- Kolom `dthdte`: 2013 nilai kosong.
- Kolom `adld3p`: 4296 nilai kosong.
- Kolom `urin1`: 3028 nilai kosong.

### Keseimbangan Kovariat Awal (Covariate Balance)
Ditemukan **38** kovariat yang memiliki Standardized Mean Difference (SMD) melebihi batas batas aman (|SMD| > 0.1), yang menunjukkan ketidakseimbangan parah sebelum penyesuaian kausal.

#### Top 10 Kovariat Paling Tidak Seimbang:

| Kovariat | SMD (Sebelum Penyesuaian) | Penjelasan Klinis |
| --- | --- | --- |
| `aps1` | +0.5014 | Skor APACHE III (keparahan penyakit - pasien RHC lebih sakit) |
| `meanbp1` | -0.4551 | Tekanan darah rata-rata hari ke-1 |
| `pafi1` | -0.4332 | Rasio PaO2/FIO2 (kadar oksigenasi darah) |
| `cat1_MOSF w/Sepsis` | +0.4148 | Kategori penyakit utama |
| `neuro` | -0.3530 | Karakteristik fisiologis / tingkat keparahan |
| `cat1_COPD` | -0.3424 | Kategori penyakit utama |
| `card` | +0.2949 | Karakteristik fisiologis / tingkat keparahan |
| `crea1` | +0.2696 | Kadar kreatinin serum (fungsi ginjal) |
| `resp` | -0.2695 | Karakteristik fisiologis / tingkat keparahan |
| `hema1` | -0.2693 | Karakteristik fisiologis / tingkat keparahan |


## Hasil Estimasi Efek Kausal - Fase 3

### 1. Ringkasan Hasil Estimasi Efek Kausal (Mortalitas 30 Hari)

| Metode | ATE | ATT | Penjelasan / Keterangan |
| --- | --- | --- | --- |
| **Naif (Korelasi)** | +5.07% | +5.07% | Mengabaikan seluruh bias seleksi |
| **Propensity Score Matching (PSM)** | - | +3.48% | ATT diukur melalui pencocokan 1:1 tanpa pengembalian |
| **Inverse Probability Weighting (IPW)** | +3.10% | +2.73% | Pembobotan peluang terbalik stabil |
| **Doubly Robust (AIPW)** | +2.95% | +3.94% | Kombinasi model propensity score & outcome |

*Catatan: Semua nilai diestimasi menggunakan regresi logistik untuk model treatment dan outcome.*

### 2. Pemeriksaan Asumsi Overlap (Positivity)
- Distribusi propensity score untuk kelompok treatment (RHC) dan kontrol (No RHC) diplot secara bertumpang-tindih menggunakan plot KDE.
- Terdapat dukungan bersama (common support) yang sangat baik pada rentang probabilitas [0.0020, 0.9875], yang berarti asumsi positivity terpenuhi dengan baik.
- Grafik visualisasi disimpan di reports/figures/05_propensity_score_overlap.png.

### 3. Evaluasi Keseimbangan Kovariat (Love Plot Comparison)
- Keseimbangan kovariat berhasil dicapai secara sempurna setelah pencocokan PSM 1:1.
- Jumlah kovariat yang tidak seimbang (|SMD| > 0.1) berkurang drastis dari 42 variabel menjadi 0 variabel.
- Seluruh bias seleksi awal (confounding by indication) berhasil dihilangkan.
- Grafik visualisasi disimpan di reports/figures/06_love_plot_comparison.png.
