# 1. Ringkasan & README Proyek

<aside>
🎯

Dokumen ringkasan proyek — jadikan ini dasar untuk file `README.md` di GitHub.

</aside>

## Judul proyek

**Membuktikan Sebab-Akibat dalam Kesehatan: Estimasi Efek Kausal dari Data Observasional**

## Latar belakang

Kebanyakan proyek data sains berhenti di *korelasi* dan *prediksi*. Padahal pertanyaan terpenting di dunia kesehatan bersifat **kausal**: *"Apakah tindakan/obat ini benar-benar MENYEBABKAN perbaikan, atau hanya kebetulan berasosiasi?"* Causal inference menjawab ini dari data observasional (tanpa uji klinis acak) menggunakan kerangka statistik formal (DAG, propensity score, dsb). Topik ini jarang digarap di portfolio, sehingga sangat menonjol dan menunjukkan kedalaman statistik.

## Pertanyaan kausal (default)

**"Apakah pemasangan Right Heart Catheterization (RHC) pada pasien ICU meningkatkan risiko mortalitas 30 hari?"**

> Ini studi kasus klasik (Connors et al., 1996): analisis naif menunjukkan RHC tampak "berbahaya", tetapi pasien yang menerima RHC memang lebih sakit (*confounding by indication*). Justru di sinilah causal inference bersinar.
> 

## Tujuan

- Merumuskan pertanyaan kausal secara formal (treatment, outcome, confounder) + membuat **DAG**.
- Mengestimasi efek kausal (**ATE/ATT**) dengan beberapa metode: propensity score matching, IPW, dan doubly robust.
- Melakukan **uji refutasi/sensitivitas** untuk menguji kekokohan hasil.
- Membandingkan hasil **naif (korelasi)** vs **kausal** untuk menunjukkan perbedaannya.
- Menyediakan demo/laporan interaktif yang menjelaskan temuan.

## Ruang lingkup

- ✅ **Termasuk:** perumusan DAG, identifikasi, estimasi efek kausal, refutasi, interpretasi.
- ❌ **Tidak termasuk:** rekomendasi klinis nyata, perangkat keras (proyek ini bersifat edukatif/portfolio).

## Target & alternatif

| Pertanyaan kausal | Dataset | Treatment → Outcome |
| --- | --- | --- |
| **RHC & mortalitas ICU (default)** | RHC (Connors et al.) — publik | RHC (ya/tidak) → meninggal (ya/tidak) |
| Merokok & kesehatan | NHANES — publik | Status merokok → tekanan darah / outcome |
| Benchmark efek kausal | IHDP / LaLonde — publik | Intervensi → outcome |

## Tech stack

- **Bahasa:** Python
- **Causal inference:** `DoWhy` (Microsoft), `EconML`, `causalml` (Uber)
- **DAG & statistik:** `networkx`, `statsmodels`, `scikit-learn`
- **Data & visualisasi:** `pandas`, `numpy`, `matplotlib`, `seaborn`
- **Demo/laporan:** Jupyter Notebook + Streamlit (opsional)

## Deliverables

- [ ]  DAG yang jelas + dokumentasi asumsi
- [ ]  Notebook/skrip estimasi efek kausal (beberapa metode)
- [ ]  Hasil uji refutasi & analisis sensitivitas
- [ ]  Perbandingan estimasi naif vs kausal
- [ ]  README + dokumentasi lengkap di GitHub

## Hasil (diisi setelah selesai)

> Contoh: *"Analisis naif menunjukkan RHC berasosiasi dengan mortalitas +X%, namun setelah penyesuaian kausal (IPW + doubly robust), estimasi ATT menjadi Y% dan tetap robust pada uji refutasi."*
>