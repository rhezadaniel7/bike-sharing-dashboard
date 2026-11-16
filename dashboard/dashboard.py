from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# ------------------------------------------------------------------
# Konfigurasi
# ------------------------------------------------------------------
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="whitegrid")
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#b8b6ae"
BASE_DIR = Path(__file__).resolve().parent  # path relatif: jalan di lokal & Streamlit Cloud
SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]
WEATHER_ORDER = ["Cerah/Berawan", "Berkabut/Mendung", "Hujan/Salju Ringan"]


@st.cache_data
def load_data():
    day = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["dteday"])
    hour = pd.read_csv(BASE_DIR / "hour_data.csv", parse_dates=["dteday", "datetime"])
    return day, hour


day_df, hour_df = load_data()

# ------------------------------------------------------------------
# Sidebar: filter
# ------------------------------------------------------------------
min_date, max_date = day_df["dteday"].min().date(), day_df["dteday"].max().date()
with st.sidebar:
    st.title("🚲 Capital Bikeshare")
    st.caption("Washington D.C., 2011–2012")
    date_range = st.date_input("Rentang tanggal", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)
    seasons = st.multiselect("Musim", SEASON_ORDER, default=SEASON_ORDER)
    st.caption("Musim dipetakan sesuai tanggal: Winter = 21 Des – 20 Mar.")

if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
    st.info("Pilih tanggal awal dan tanggal akhir pada sidebar.")
    st.stop()

start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
day = day_df[day_df["dteday"].between(start, end) & day_df["season_label"].isin(seasons)]
hour = hour_df[hour_df["dteday"].between(start, end) & hour_df["season_label"].isin(seasons)]

if day.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ------------------------------------------------------------------
# Header & metrik
# ------------------------------------------------------------------
st.title("Dashboard Analisis Bike Sharing")
st.caption(f"Periode {start:%d %b %Y} – {end:%d %b %Y} · {len(day):,} hari · Musim: {', '.join(seasons)}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total penyewaan", f"{day['cnt'].sum():,}")
c2.metric("Rata-rata per hari", f"{day['cnt'].mean():,.0f}")
c3.metric("Pengguna registered", f"{day['registered'].sum() / day['cnt'].sum():.1%}")
c4.metric("Pengguna casual", f"{day['casual'].sum() / day['cnt'].sum():.1%}")

# Tren bulanan
st.subheader("Tren Penyewaan Bulanan")
monthly = day.set_index("dteday").resample("MS")[["casual", "registered"]].sum()
fig, ax = plt.subplots(figsize=(12, 3.8))
ax.plot(monthly.index, monthly["registered"], color=BLUE, marker="o", linewidth=2, label="Registered")
ax.plot(monthly.index, monthly["casual"], color=ORANGE, marker="o", linewidth=2, label="Casual")
ax.set_ylabel("Total penyewaan per bulan")
ax.set_ylim(0, None)
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
ax.legend(frameon=False)
st.pyplot(fig)

tab1, tab2, tab3, tab4 = st.tabs(["1 · Hari Kerja vs Libur", "2 · Jam Sibuk", "3 · Cuaca & Musim",
                                  "Analisis Lanjutan (Clustering)"])

# ------------------------------------------------------------------
# Pertanyaan 1
# ------------------------------------------------------------------
with tab1:
    st.markdown("**Bagaimana rata-rata penyewaan harian hari kerja vs libur untuk pengguna casual dan registered?**")
    q1 = day.groupby("day_type")[["casual", "registered"]].mean()
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        q1.rename(columns=str.capitalize).plot(kind="bar", ax=ax, color=[ORANGE, BLUE], width=0.7,
                                               edgecolor="white", linewidth=2)
        for cont in ax.containers:
            ax.bar_label(cont, fmt="{:,.0f}", padding=3, fontsize=9)
        ax.set_title("Rata-rata penyewaan per hari", fontweight="bold")
        ax.set_xlabel(None)
        ax.set_ylabel("Penyewaan per hari")
        ax.set_ylim(0, q1.values.max() * 1.15)
        ax.tick_params(axis="x", rotation=0)
        ax.legend(title="Tipe pengguna", frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2)
        st.pyplot(fig)
    with col2:
        share = day.groupby("day_type")[["casual", "registered"]].sum()
        share = share.div(share.sum(axis=1), axis=0) * 100
        fig, ax = plt.subplots(figsize=(6, 4.2))
        share.rename(columns=str.capitalize).plot(kind="barh", stacked=True, ax=ax, color=[ORANGE, BLUE],
                                                  edgecolor="white", linewidth=2)
        for i, (c, r) in enumerate(share.values):
            ax.text(c / 2, i, f"{c:.1f}%", ha="center", va="center", color="white", fontweight="bold")
            ax.text(c + r / 2, i, f"{r:.1f}%", ha="center", va="center", color="white", fontweight="bold")
        ax.set_title("Porsi tipe pengguna (%)", fontweight="bold")
        ax.set_xlim(0, 100)
        ax.set_xlabel("Porsi dari total penyewaan (%)")
        ax.set_ylabel(None)
        ax.legend(title="Tipe pengguna", frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
        st.pyplot(fig)
    st.info("Pengguna casual melonjak di hari libur, sedangkan registered mendominasi hari kerja "
            "(periode penuh 2011–2012: porsi casual 13,2% → 31,7%). Hari libur adalah momen terbaik untuk promo konversi member.")

# ------------------------------------------------------------------
# Pertanyaan 2
# ------------------------------------------------------------------
with tab2:
    st.markdown("**Pada jam berapa puncak penyewaan terjadi pada hari kerja vs hari libur?**")
    pola = hour.pivot_table(index="hr", columns="day_type", values="cnt", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(12, 4.5))
    warna = {"Hari Kerja": BLUE, "Libur/Akhir Pekan": ORANGE}
    for tipe in pola.columns:
        ax.plot(pola.index, pola[tipe], marker="o", markersize=5, linewidth=2, color=warna[tipe], label=tipe)
        jam = pola[tipe].idxmax()
        ax.annotate(f"{jam:02d}.00\n{pola.loc[jam, tipe]:,.0f}/jam", xy=(jam, pola.loc[jam, tipe]),
                    xytext=(0, 10), textcoords="offset points", ha="center", fontsize=9,
                    fontweight="bold", color=warna[tipe])
    ax.axvspan(7, 9, color=GRAY, alpha=0.2)
    ax.axvspan(16, 19, color=GRAY, alpha=0.2)
    ax.set_xticks(range(24))
    ax.set_xlabel("Jam (0–23)")
    ax.set_ylabel("Rata-rata penyewaan per jam")
    ax.set_ylim(0, pola.values.max() * 1.2)
    ax.legend(frameon=False)
    st.pyplot(fig)
    st.info("Hari kerja punya dua puncak komuter (±08.00 dan ±17.00, area abu-abu), hari libur memuncak landai "
            "di 12.00–15.00. Redistribusi armada dilakukan sebelum 07.00 dan 16.00; perawatan di 00.00–05.00.")

# ------------------------------------------------------------------
# Pertanyaan 3
# ------------------------------------------------------------------
with tab3:
    st.markdown("**Seberapa besar penurunan penyewaan saat hujan/salju ringan dibanding cerah di tiap musim?**")
    heat = day.pivot_table(index="season_label", columns="weather_label", values="cnt", aggfunc="mean")
    heat = heat.reindex(index=[s for s in SEASON_ORDER if s in heat.index],
                        columns=[w for w in WEATHER_ORDER if w in heat.columns])
    col1, col2 = st.columns([1.3, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(7, 4.2))
        sns.heatmap(heat, annot=True, fmt=",.0f", cmap="Blues", linewidths=2, linecolor="white",
                    cbar_kws={"label": "Rata-rata penyewaan per hari"}, ax=ax)
        ax.set_title("Rata-rata sewa harian per musim & cuaca", fontweight="bold")
        ax.set_xlabel("Kondisi cuaca")
        ax.set_ylabel("Musim")
        ax.tick_params(axis="y", rotation=0)
        st.pyplot(fig)
    with col2:
        if {"Cerah/Berawan", "Hujan/Salju Ringan"}.issubset(heat.columns):
            drop = ((heat["Hujan/Salju Ringan"] / heat["Cerah/Berawan"] - 1) * 100).dropna()
            if not drop.empty:
                fig, ax = plt.subplots(figsize=(6, 4.2))
                bars = ax.barh(drop.index, drop.abs(), color=[ORANGE if v == drop.min() else GRAY for v in drop],
                               edgecolor="white", linewidth=2)
                ax.bar_label(bars, labels=[f"-{v:.0f}%" for v in drop.abs()], padding=3, fontweight="bold")
                ax.invert_yaxis()
                ax.set_xlim(0, 100)
                ax.set_title("Penurunan saat hujan/salju vs cerah", fontweight="bold")
                ax.set_xlabel("Penurunan rata-rata sewa harian (%)")
                st.pyplot(fig)
        else:
            st.caption("Tidak ada hari hujan/salju ringan pada filter ini.")
    n_rain = (day["weather_label"] == "Hujan/Salju Ringan").sum()
    st.info(f"Hujan/salju ringan memangkas penyewaan di setiap musim. Catatan: hanya {n_rain} hari hujan/salju "
            "ringan pada filter ini, jadi persentase per musim bersifat indikatif.")

# ------------------------------------------------------------------
# Analisis lanjutan
# ------------------------------------------------------------------
with tab4:
    st.markdown("**Clustering manual (binning) tanpa machine learning**")
    col1, col2 = st.columns(2)
    with col1:
        bins = [0, 10, 20, 30, 41]
        labels = ["Dingin (≤10°C)", "Sejuk (10–20°C)", "Hangat (20–30°C)", "Panas (>30°C)"]
        suhu = (day.assign(kategori=pd.cut(day["temp_c"], bins=bins, labels=labels))
                .groupby("kategori", observed=True)["cnt"].agg(["mean", "size"]))
        fig, ax = plt.subplots(figsize=(6, 4.2))
        bars = ax.bar(suhu.index.astype(str), suhu["mean"],
                      color=[BLUE if v == suhu["mean"].max() else GRAY for v in suhu["mean"]],
                      edgecolor="white", linewidth=2)
        ax.bar_label(bars, labels=[f"{m:,.0f}\n({n} hari)" for m, n in zip(suhu["mean"], suhu["size"])],
                     padding=3, fontsize=8)
        ax.set_title("Rata-rata sewa harian per kategori suhu", fontweight="bold")
        ax.set_ylabel("Penyewaan per hari")
        ax.set_ylim(0, suhu["mean"].max() * 1.25)
        ax.tick_params(axis="x", rotation=15)
        st.pyplot(fig)
    with col2:
        seg_bins = [-1, 5, 9, 15, 19, 23]
        seg_labels = ["Dini Hari\n(00–05)", "Pagi Sibuk\n(06–09)", "Siang\n(10–15)", "Sore Sibuk\n(16–19)", "Malam\n(20–23)"]
        seg = (hour.assign(segmen=pd.cut(hour["hr"], bins=seg_bins, labels=seg_labels))
               .groupby("segmen", observed=True)[["casual", "registered"]].sum())
        seg = seg / seg.sum() * 100
        fig, ax = plt.subplots(figsize=(6, 4.2))
        seg.rename(columns=str.capitalize).plot(kind="bar", ax=ax, color=[ORANGE, BLUE], width=0.75,
                                                edgecolor="white", linewidth=2)
        ax.set_title("Porsi sewa per segmen waktu", fontweight="bold")
        ax.set_xlabel(None)
        ax.set_ylabel("Porsi dari total tipe pengguna (%)")
        ax.tick_params(axis="x", rotation=0)
        ax.legend(title="Tipe pengguna", frameon=False)
        st.pyplot(fig)

    st.markdown("**Profil hari berdasarkan tingkat permintaan (dibagi 3 kelompok sama besar)**")
    if day["cnt"].nunique() >= 3:
        grp = day.assign(tingkat=pd.qcut(day["cnt"], q=3, labels=["Rendah", "Sedang", "Tinggi"], duplicates="drop"))
        profil = grp.groupby("tingkat", observed=True).agg(
            jumlah_hari=("cnt", "size"),
            rentang_sewa=("cnt", lambda x: f"{x.min():,} – {x.max():,}"),
            rata2_sewa=("cnt", "mean"),
            rata2_suhu_c=("temp_c", "mean"),
            porsi_cerah_pct=("weather_label", lambda x: (x == "Cerah/Berawan").mean() * 100),
            porsi_winter_pct=("season_label", lambda x: (x == "Winter").mean() * 100),
        ).round(1)
        st.dataframe(profil, width="stretch")

st.caption("Sumber data: Bike Sharing Dataset (Fanaee-T & Gama, 2013) · Dibuat oleh Daniel (DS234B6Y0405)")
