# Bike Sharing Data Analysis Dashboard 🚲

Proyek akhir **Belajar Analisis Data dengan Python** (Dicoding) — analisis data penyewaan sepeda Capital Bikeshare, Washington D.C., tahun 2011–2012.

- **Nama:** Daniel
- **ID Dicoding:** DS234B6Y0405
- **Dataset:** [Bike Sharing Dataset (Kaggle)](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset/data)

## Pertanyaan Bisnis
1. Bagaimana perbandingan rata-rata penyewaan harian hari kerja vs hari libur/akhir pekan untuk pengguna casual dan registered (Jan 2011 – Des 2012)?
2. Pada jam berapa puncak penyewaan per jam terjadi pada hari kerja vs hari libur sepanjang tahun 2012?
3. Berapa persen penurunan rata-rata penyewaan harian saat hujan/salju ringan dibanding cuaca cerah pada setiap musim (2011–2012)?

## Struktur Folder
```
submission
├── dashboard
│   ├── dashboard.py      # aplikasi Streamlit
│   ├── main_data.csv     # data harian bersih (hasil notebook)
│   └── hour_data.csv     # data per jam bersih (hasil notebook)
├── data
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.12
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
cd submission
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run Streamlit App
Jalankan dari folder `submission`:
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`.

## Fitur Dashboard
- Filter rentang tanggal dan musim di sidebar.
- Metrik ringkas: total penyewaan, rata-rata per hari, porsi casual vs registered.
- Tren penyewaan bulanan.
- Tab jawaban Pertanyaan 1, 2, 3 dan tab analisis lanjutan (clustering manual dengan binning).
