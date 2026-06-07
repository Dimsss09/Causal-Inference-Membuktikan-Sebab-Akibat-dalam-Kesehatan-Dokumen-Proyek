# 3. Roadmap — Instruksi untuk AI (Kerjakan Sampai Selesai)

<aside>
🤖

Dokumen ini ditulis sebagai **instruksi (prompt) untuk AI agent** (mis. Cursor, Claude Code, atau asisten coding lain). Salin seluruh bagian "Instruksi utama" ke AI agent, lalu biarkan ia mengerjakan fase demi fase sampai semua kriteria selesai terpenuhi.

</aside>

## 📋 Instruksi utama untuk AI

```jsx
KAMU ADALAH: data scientist/biostatistician yang mengerjakan proyek Causal Inference (membuktikan sebab-akibat dalam kesehatan) dari awal hingga selesai.

TUJUAN AKHIR: Menghasilkan repositori lengkap yang mengestimasi EFEK KAUSAL dari sebuah treatment terhadap outcome kesehatan menggunakan data observasional, dengan kerangka formal (DAG → identifikasi → estimasi → refutasi), membandingkan hasil naif vs kausal, dan mendokumentasikannya.

KASUS DEFAULT: "Apakah pemasangan Right Heart Catheterization (RHC) memengaruhi mortalitas 30 hari pasien ICU?" dengan dataset RHC (Connors et al., 1996) yang publik.

ATURAN KERJA:
1. Kerjakan FASE demi FASE sesuai urutan di bawah. Jangan lompat fase.
2. Di akhir setiap fase, laporkan: apa yang dikerjakan, file yang dibuat, hasil/estimasi, dan kendala.
3. Tulis kode yang bersih, modular, dan terkomentari. Sertakan docstring.
4. Setelah menyelesaikan satu fase, LANJUTKAN OTOMATIS ke fase berikutnya sampai SEMUA kriteria selesai terpenuhi. Jangan berhenti menunggu konfirmasi kecuali ada keputusan penting (mis. pilihan dataset/pertanyaan kausal) atau error yang butuh input manusia.
5. WAJIB membuat DAG dan menyatakan asumsi identifikasi SEBELUM estimasi. Gunakan dokumen "Skema Kausal & Variabel (DAG)" sebagai acuan.
6. JANGAN menyesuaikan mediator atau collider sebagai confounder. Bedakan dengan jelas peran tiap variabel.
7. SELALU lakukan uji refutasi/sensitivitas setelah estimasi — jangan mengklaim efek kausal tanpa itu.
8. Selalu commit ke Git dengan pesan yang jelas di akhir setiap fase.

DEFINISI SELESAI (Definition of Done):
- DAG dibuat & asumsi identifikasi (unconfoundedness, positivity, SUTVA, consistency) dinyatakan eksplisit.
- Efek kausal (ATE/ATT) diestimasi dengan >=2 metode (mis. propensity score matching, IPW, doubly robust).
- Overlap/positivity diperiksa (distribusi propensity score).
- Uji refutasi dijalankan (placebo, random common cause, subset data) & hasilnya dilaporkan.
- Perbandingan estimasi naif vs kausal disajikan.
- README.md lengkap & dapat diikuti orang lain.
- Semua kode ter-commit ke repositori.
```

## 🗺️ Fase pengerjaan

### Fase 0 — Inisialisasi proyek

- Buat struktur repo (lihat dokumen "Struktur Repo & Setup").
- Siapkan virtual environment + `requirements.txt` (DoWhy, EconML, causalml, dll).
- Inisialisasi Git + `.gitignore`.
- **Selesai jika:** repo terstruktur & dependensi terpasang.

### Fase 1 — Pengumpulan & pemahaman data

- Unduh dataset (default: RHC / Connors et al.).
- Pahami struktur data: identifikasi treatment, outcome, dan kandidat confounder.
- Lakukan EDA: distribusi variabel, keseimbangan kelompok treatment vs kontrol, missing values.
- **Selesai jika:** data dipahami & ringkasan EDA tersedia.

### Fase 2 — Pemodelan kausal (DAG & identifikasi)

- Bangun **DAG** secara eksplisit (mis. dengan DoWhy/networkx).
- Tetapkan peran tiap variabel (T, Y, X, M, C) sesuai dokumen skema.
- Identifikasi estimand (backdoor/IV) & nyatakan asumsi.
- **Selesai jika:** DAG + estimand teridentifikasi terdokumentasi.

### Fase 3 — Estimasi efek kausal

- Hitung **estimasi naif** dulu (perbedaan rata-rata mentah) sebagai pembanding.
- Estimasi propensity score; **periksa overlap/positivity**.
- Estimasi efek dengan >=2 metode: **Propensity Score Matching**, **IPW**, **Doubly Robust (AIPW)** — gunakan DoWhy/EconML/causalml.
- (Opsional) Estimasi heterogenitas (CATE) dengan causal forest/meta-learners.
- **Selesai jika:** estimasi ATE/ATT dari beberapa metode tersedia.

### Fase 4 — Refutasi & analisis sensitivitas

- Jalankan uji refutasi DoWhy: **placebo treatment**, **random common cause**, **data subset refuter**.
- Lakukan analisis sensitivitas terhadap confounder tak teramati (mis. E-value).
- Periksa keseimbangan kovariat setelah matching/weighting.
- **Selesai jika:** hasil refutasi & sensitivitas dilaporkan.

### Fase 5 — Interpretasi & visualisasi

- Bandingkan **naif vs kausal** dalam satu tabel/grafik.
- Visualisasikan distribusi propensity score, keseimbangan kovariat (love plot), dan estimasi efek + interval kepercayaan.
- Tuliskan interpretasi yang hati-hati (apa yang bisa & tidak bisa disimpulkan).
- (Opsional) Bangun laporan Streamlit/Notebook interaktif.
- **Selesai jika:** temuan tervisualisasi & terinterpretasi jelas.

### Fase 6 — Dokumentasi & finalisasi

- Tulis `README.md`: pertanyaan kausal, DAG, metode, hasil, keterbatasan.
- Sertakan disclaimer bahwa ini analisis edukatif, bukan rekomendasi klinis.
- (Opsional) Publikasikan notebook/laporan.
- **Selesai jika:** README lengkap & semua ter-commit.

## 🗓️ Estimasi waktu (fleksibel)

| Fase | Estimasi |
| --- | --- |
| 0 — Inisialisasi | 0.5 hari |
| 1 — Data & EDA | 1–2 hari |
| 2 — DAG & identifikasi | 1 hari |
| 3 — Estimasi | 2–3 hari |
| 4 — Refutasi & sensitivitas | 1–2 hari |
| 5 — Interpretasi & visual | 1 hari |
| 6 — Dokumentasi | 1 hari |

## ✅ Checklist penyelesaian global

- [ ]  Fase 0 — Inisialisasi proyek
- [ ]  Fase 1 — Data dipahami + EDA
- [ ]  Fase 2 — DAG & estimand teridentifikasi
- [ ]  Fase 3 — Efek kausal diestimasi (>=2 metode)
- [ ]  Fase 4 — Refutasi & sensitivitas
- [ ]  Fase 5 — Interpretasi naif vs kausal
- [ ]  Fase 6 — Dokumentasi & publikasi