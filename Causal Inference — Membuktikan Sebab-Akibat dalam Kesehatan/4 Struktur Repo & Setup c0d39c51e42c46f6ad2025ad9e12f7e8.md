# 4. Struktur Repo & Setup

<aside>
🧱

Panduan struktur folder repositori & penyiapan lingkungan agar proyek rapi dan mudah diikuti.

</aside>

## Struktur folder

```
causal-inference-health/
├── data/
│   ├── raw/              # data mentah (RHC/NHANES) — jangan di-commit
│   └── processed/        # data setelah pembersihan
├── notebooks/
│   ├── 01_eda.ipynb              # eksplorasi data
│   ├── 02_dag_identification.ipynb
│   ├── 03_estimation.ipynb
│   └── 04_refutation.ipynb
├── src/
│   ├── data_loader.py    # muat & bersihkan data
│   ├── dag.py            # definisi DAG & estimand
│   ├── estimators.py     # PSM, IPW, doubly robust
│   ├── refute.py         # uji refutasi & sensitivitas
│   └── plots.py          # love plot, distribusi PS, dll
├── reports/
│   ├── figures/          # grafik hasil
│   └── results.md        # ringkasan estimasi naif vs kausal
├── models/               # objek model tersimpan (opsional)
├── app.py                # demo/laporan Streamlit (opsional)
├── requirements.txt
├── .gitignore
└── README.md
```

## requirements.txt

```
pandas
numpy
scipy
scikit-learn
statsmodels
dowhy
econml
causalml
networkx
matplotlib
seaborn
jupyter
streamlit
```

## Langkah setup

```bash
# 1. Buat & aktifkan virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Pasang dependensi
pip install -r requirements.txt

# 3. Inisialisasi Git
git init
git add .
git commit -m "Inisialisasi proyek causal inference"

# 4. Jalankan notebook / demo
jupyter notebook
# atau
streamlit run app.py
```

## .gitignore

```
venv/
__pycache__/
*.pyc
data/raw/
.ipynb_checkpoints/
models/*.pkl
.env
```

<aside>
💡

**Tips:** Catat sumber & versi dataset di `README.md`. Untuk causalml yang kadang sulit dipasang, alternatifnya cukup pakai `dowhy` + `econml` saja — keduanya sudah cukup untuk PSM, IPW, dan doubly robust.

</aside>