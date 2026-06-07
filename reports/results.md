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
