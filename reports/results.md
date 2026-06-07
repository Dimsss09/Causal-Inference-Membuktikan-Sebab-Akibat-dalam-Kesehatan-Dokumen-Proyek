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
Ditemukan **35** kovariat yang memiliki Standardized Mean Difference (SMD) melebihi batas batas aman (|SMD| > 0.1), yang menunjukkan ketidakseimbangan parah sebelum penyesuaian kausal.

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


## Hasil Pemodelan Kausal (DAG & Identifikasi) - Fase 2

### 1. Struktur Directed Acyclic Graph (DAG)
Kami telah memodelkan relasi sebab-akibat secara formal menggunakan Directed Acyclic Graph (DAG):
- **Treatment (T):** Pemasangan Right Heart Catheterization (RHC) (	reatment).
- **Outcome (Y):** Mortalitas 30 Hari (outcome).
- **Mediator (M):** Perubahan Tatalaksana Medis. Ini dilewati untuk mengukur *Total Causal Effect* (efek total intervensi RHC).
- **Confounders (X):** 68 variabel klinis (usia, skor keparahan APACHE III, vital signs, komorbiditas, diagnosis utama, dll).
- **Jalur Belakang (Backdoor Path):** T <-- X --> Y merupakan sumber bias utama (confounding by indication).

Grafik visualisasi DAG yang disederhanakan telah disimpan di reports/figures/04_causal_dag.png.

### 2. Hasil Identifikasi Efek Kausal (DoWhy)
- **Metode Identifikasi:** Backdoor Criterion.
- **Estimand Utama:** Nonparametric ATE / ATT.
- **Kondisi Identifikasi:** Efek kausal total dari RHC terhadap mortalitas dapat diidentifikasi secara unik jika kita menyesuaikan (conditioning on) seluruh 68 confounder yang diidentifikasi.
- **Asumsi Causal:**
  1. Unconfoundedness (Ignorability): Tidak ada confounder tersembunyi.
  2. Positivity (Overlap): Distribusi peluang menerima treatment dan kontrol bernilai non-nol untuk setiap strata confounder.
