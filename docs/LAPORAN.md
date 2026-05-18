# Laporan Proyek Akhir — Analisis dan Visualisasi TLC Trip Data

**Mata Kuliah:** Rekayasa Data dan Visualisasi (RDV)
**Kelas:** TIF-A
**Tahun:** 2026

> Template laporan. Konversi ke `.docx`/`.pdf` saat submission. Istilah teknis
> bahasa Inggris (data lake, medallion, pipeline, dst.) sengaja tidak
> diterjemahkan untuk menjaga kejelasan.

---

## 1. Identitas Tim

| NIM | Nama |
| --- | --- |
| 245150201111042 | ANINDHITA FAIZA AULIA |
| 245150201111043 | ANIZA HELWA MAHANANI |
| 245150207111046 | MUHAMAD FAHRY PRATAMA PUTRA |
| 245150201111002 | MUHAMMAD ATHA TSAQIF |
| 245150200111008 | NAFIS NAUFAL RAHMAN |
| 245150200111061 | RICHARD SAMUEL HATANE |

### 1.1 Pembagian Tugas

| Peran | Anggota | Tanggung Jawab Utama |
| --- | --- | --- |
| Data Architect / Project Lead | NAFIS NAUFAL RAHMAN | Desain arsitektur pipeline, koordinasi tim, repository setup, dokumentasi |
| Data Engineer (Ingestion) | MUHAMAD FAHRY PRATAMA PUTRA | Script ingestion TLC + Open-Meteo + taxi zones, Prefect flow |
| Data Engineer (Cleaning + Transformation) | MUHAMMAD ATHA TSAQIF | Bronze→silver cleaning, dbt models, DuckDB schema, data quality tests |
| ML Engineer | ANIZA HELWA MAHANANI | Clustering (K-Means/GMM), pemilihan model via silhouette score, profil archetype |
| Data Analyst (Dashboard) | RICHARD SAMUEL HATANE | Streamlit pages, Folium choropleth, Pydeck 3D map, theming |
| Data Analyst (Analysis & Report) | ANINDHITA FAIZA AULIA | Analisis hasil, narasi visualisasi, finalisasi laporan |

---

## 2. Latar Belakang dan Tujuan

### 2.1 Latar Belakang
Industri ride-hailing dan taksi di kota besar menghadapi tantangan klasik:
demand yang tidak merata secara spasial maupun temporal, ditambah pengaruh
cuaca yang sulit diprediksi. NYC Taxi & Limousine Commission (TLC) merilis
trip-level data secara terbuka, menjadikan dataset ini playground ideal untuk
membangun pipeline data engineering end-to-end yang relevan dengan kasus nyata.

### 2.2 Rumusan Masalah
> Di mana, kapan, dan pada kondisi cuaca seperti apa demand Yellow Taxi NYC
> paling tinggi — dan bagaimana driver/dispatcher dapat mengantisipasinya?

### 2.3 Tujuan Proyek
1. **Spasial.** Mengelompokkan (clustering) 263 NYC taxi zones menjadi
   beberapa operational profile (commuter, nightlife, airport, weather-sensitive,
   …) berdasarkan perilaku trip dan sensitivitas cuaca.
2. **Temporal.** Mengkuantifikasi pengaruh jam, hari, dan cuaca terhadap
   demand serta durasi perjalanan.
3. **Operasional.** Menerjemahkan hasil clustering menjadi rekomendasi nyata
   per segmen zona (alokasi armada, waktu operasi, respons cuaca).

### 2.4 Batasan
- Dataset: **Yellow Taxi** (Manhattan-centric) periode **Januari – Juni 2025**.
- Cakupan geografis: 263 taxi zones standar TLC.
- Data cuaca: Open-Meteo Historical Weather API, koordinat midtown Manhattan
  (40.758, −73.986).
- Pemodelan dilakukan pada skala per-zone untuk clustering; analisis temporal
  pada skala citywide hourly.

---

## 3. Arsitektur Pipeline

### 3.1 Diagram

> Sisipkan screenshot diagram dari `README.md`.

### 3.2 Alur Data

1. **Ingestion** — TLC parquet, weather API, dan zone shapefile diunduh ke
   `data/bronze/`.
2. **Cleaning** — DuckDB membersihkan anomali dan menghitung kolom turunan;
   hasil disimpan ke `data/silver/`.
3. **Transformation (dbt)** — model `staging → intermediate → marts`
   menghasilkan tabel siap-analisis di DuckDB warehouse.
4. **ML** — clustering dilatih dari marts, hasil dan profil cluster disimpan
   ke `data/marts/`.
5. **Serving** — Streamlit menampilkan dashboard interaktif dengan peta.

### 3.3 Tools yang Digunakan

| Layer | Tool | Justifikasi |
| --- | --- | --- |
| Orchestration | Prefect 3 | Python-native, mudah di-deploy lokal, scheduler built-in |
| Storage | DuckDB + Parquet (medallion) | Tidak butuh server; sangat cepat untuk analytical workload |
| Transformation | dbt-duckdb | SQL deklaratif, schema test built-in, auto-generate lineage |
| Geospatial | GeoPandas, Folium, Pydeck | Peta interaktif tanpa GIS server |
| ML | scikit-learn (K-Means, GMM) | Multi-algorithm comparison, pemilihan via silhouette score |
| Dashboard | Streamlit + Plotly | Dashboard interaktif multi-halaman dengan kode Python murni |
| Packaging | uv, pyproject.toml | Manajer dependensi Python tercepat di 2026 |

---

## 4. Dataset

### 4.1 NYC TLC Yellow Trip Record
- Sumber: <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>
- Periode: Jan–Jun 2025 (6 file parquet bulanan; ~24 juta baris mentah,
  ~22 juta baris setelah cleaning).
- Kolom utama: `VendorID`, `tpep_pickup_datetime`, `tpep_dropoff_datetime`,
  `passenger_count`, `trip_distance`, `PULocationID`, `DOLocationID`,
  `payment_type`, `fare_amount`, `tip_amount`, `total_amount`.

### 4.2 Open-Meteo Historical Weather
- Sumber: <https://open-meteo.com/en/docs/historical-weather-api>
- Resolusi: hourly. Variabel: `temperature_2m`, `apparent_temperature`,
  `precipitation`, `rain`, `snowfall`, `cloud_cover`, `wind_speed_10m`,
  `wind_gusts_10m`, `visibility`, `weather_code`.
- Lokasi: koordinat Manhattan midtown (40.758, −73.986).

### 4.3 NYC Taxi Zones Shapefile
- Sumber: TLC CloudFront mirror.
- Konten: polygon untuk 263 zone (1–265, dengan beberapa ID kosong).

---

## 5. Tahapan Pengerjaan

### 5.1 Data Ingestion
Implementasi: `src/nyc_tlc/ingest/{tlc,weather,zones}.py`.

> Sertakan screenshot output `make ingest` dan struktur folder `data/bronze/`
> setelah ingest selesai.

Fitur:
- Streaming download via `requests` agar tidak memakan RAM.
- Skip file yang sudah ada (idempotent).
- Date-bounds otomatis untuk panggilan weather API.

### 5.2 Preprocessing dan Cleaning
Implementasi: `src/nyc_tlc/clean/run.py`.

Anomali yang ditangani:

| Anomali | Aksi |
| --- | --- |
| `tpep_pickup_datetime` atau `tpep_dropoff_datetime` NULL | DROP |
| Dropoff ≤ pickup | DROP |
| `trip_distance` ≤ 0 atau > 200 mil | DROP |
| `fare_amount` negatif atau > 2000 | DROP |
| `total_amount` negatif atau > 3000 | DROP |
| `PULocationID` / `DOLocationID` di luar 1–265 | DROP |
| `trip_duration_min` ≤ 0 atau > 720 menit | DROP |
| `passenger_count = 0` (driver tidak input) | NULL-out |
| `passenger_count` > 9 | NULL-out |
| `avg_speed_mph` > 100 (GPS / clock anomaly) | DROP |

Derived columns: `trip_duration_min`, `avg_speed_mph`, `pickup_hour`,
`pickup_dow`, `is_weekend`.

> Sertakan screenshot perbandingan jumlah baris bronze → silver.

### 5.3 Pemodelan dan Penyimpanan
Implementasi: `dbt_project/`, DuckDB warehouse di `data/warehouse.duckdb`.

Struktur:
- **Staging** (view) — `stg_yellow_trips`, `stg_weather_hourly`.
- **Intermediate** (table) — `int_trips_with_weather`, `int_zone_hourly`.
- **Marts** (table) — `dim_zone`, `fct_zone_features`, `fct_hourly_demand`,
  `fct_flow_od`.

> Sertakan screenshot dbt lineage graph dan tabel marts.

### 5.4 Analisis
Implementasi: `src/nyc_tlc/ml/` dan model dbt marts.

Pertanyaan analitis yang dijawab:
- Zona mana yang paling aktif, paling jauh, paling sensitif terhadap cuaca?
  (Mart `fct_zone_features` + cluster labels.)
- Berapa peningkatan demand saat hujan? (Field `rain_demand_ratio`.)
- Hari/jam apa peak demand? (Mart `fct_hourly_demand` + halaman Weather
  Impact dashboard.)

> Sertakan screenshot tabel cluster profile dan perbandingan silhouette score
> K-Means vs GMM.

### 5.5 Visualisasi
Implementasi: `src/nyc_tlc/dashboard/`.

Halaman dashboard:
1. **Home** — KPI strip + time-series demand harian + heatmap hari×jam.
2. **Geospatial** — Folium choropleth (warna zone berdasar cluster atau
   metrik lain) + Pydeck 3D extruded layer + top OD corridors.
3. **Weather Impact** — bar/scatter trip vs cuaca dan suhu.
4. **ML Insights** — tabel ringkasan segmen + deskripsi archetype + rekomendasi
   armada + evidence chart σ-deviation.

Filter interaktif: tipe hari (semua/weekday/weekend), metrik pewarnaan zone,
jumlah koridor yang ditampilkan.

> Sertakan screenshot setiap halaman dashboard.

---

## 6. Bonus

### 6.1 Integrasi Data Eksternal (+10)
Open-Meteo Historical Weather API diintegrasikan pada tahap ingestion
(`src/nyc_tlc/ingest/weather.py`) dan di-join ke trip pada model dbt
`int_trips_with_weather` melalui kolom `pickup_hour_ts ↔ weather_ts`.
Dashboard halaman **Weather Impact** memvisualisasikan pengaruh cuaca
terhadap demand.

### 6.2 Machine Learning (+10)
Zone clustering menggunakan dua algoritma yang dibandingkan: **K-Means**
dan **Gaussian Mixture**, masing-masing di-sweep untuk k ∈ [3, 10].
Pemenang dipilih berdasarkan **silhouette score** tertinggi; Davies–Bouldin
dan Calinski–Harabasz juga dihitung untuk cross-checking.

#### 6.2.1 Feature engineering
Fitur count yang sangat right-skewed (`total_trips`) di-transform dengan
`log1p` sebelum standardisasi. Tanpa transform ini, jarak Euclidean
didominasi oleh satu sumbu volume sehingga clustering hanya menghasilkan
kelompok kasar besar/sedang/kecil. Setelah `log1p`, fitur perilaku
(distribusi jam, tip ratio, sensitivitas cuaca) ikut berperan secara
proporsional.

#### 6.2.2 Penamaan cluster otomatis
Nama cluster **tidak ditentukan manual**. Mekanismenya (lihat
`src/nyc_tlc/ml/profiles.py`):

1. Rata-rata tiap fitur dihitung per cluster, lalu dibandingkan terhadap
   rata-rata kota dengan z-score.
2. Fitur dengan z-score positif tertinggi pada tiap cluster dipetakan ke
   nama archetype tetap. Contoh: z-score tertinggi pada `avg_distance` dan
   `avg_fare` → "Airport & Long-Haul Gateway"; `share_morning_rush` atau
   `share_evening_rush` tertinggi → "Commuter Corridor".
3. Jika tidak ada fitur yang menyimpang di atas ambang batas (z > 0.2),
   cluster diberi nama "Low-Activity Residential".

Katalog archetype: High-Volume Urban Core, Airport & Long-Haul Gateway,
Commuter Corridor, Nightlife & Weekend Hotspot, Midday Business District,
Weather-Sensitive Demand, Low-Activity Residential.

Tabel `data/marts/zone_cluster_profiles.parquet` menyimpan untuk setiap
cluster: nama archetype, jumlah zone, rata-rata dan z-score tiap fitur.

> Sertakan screenshot tabel cluster profiles dan evidence chart σ-deviation
> dari halaman ML Insights dashboard.

---

## 7. Kesimpulan dan Future Work

### 7.1 Temuan Utama

**Skala dan kualitas data.** Dari ~24 juta baris perjalanan mentah
(Yellow Taxi, Jan–Jun 2025), ~22 juta baris (~91%) lolos proses cleaning.
Sekitar 8,6% baris dibuang sebagai anomali — timestamp invalid, dropoff
sebelum pickup, jarak/tarif di luar batas wajar, dan kecepatan > 100 mph.

**Pola temporal.** Demand memuncak pada **pukul 18:00** dan terendah pada
**pukul 04:00** — rasio hampir **10×**. Demand akhir pekan dan hari kerja
relatif seimbang; perbedaan besar ada pada distribusi jam (nightlife vs
commute peak).

**Pengaruh cuaca.** Rata-rata demand per jam **tertinggi saat hujan**
(+sekitar 22% dibanding cuaca cerah) — konsisten dengan hipotesis bahwa
penumpang lebih memilih taksi saat cuaca buruk.

**Segmentasi zona.** 263 zona terbagi menjadi beberapa segmen yang
geografis koheren: inti Manhattan sebagai High-Volume Urban Core, zona luar
sebagai Low-Activity Residential, dan kelompok zona yang demand-nya
merespons secara signifikan terhadap hujan/salju sebagai
Weather-Sensitive Demand.

**Koridor tersibuk.** Aliran trip terbesar terkonsentrasi di Upper East Side
— pasangan koridor Upper East Side South ↔ Upper East Side North menjadi
yang terpadat di seluruh kota.

### 7.2 Future Work
- Clustering per-borough untuk granularitas lebih tinggi.
- Penambahan event calendar (konser, olahraga, parade) sebagai fitur eksternal.
- Forecasting demand per jam (citywide atau per-zone).
- Migrasi DuckDB lokal ke MotherDuck untuk multi-user.

---

## 8. Lampiran

- **Repository:** \<isi link GitHub setelah push\>
- **Source code archive:** `[TP][RDV-TIF-A] <NamaKetua>.zip`
- **Dashboard demo:** `make dashboard` → <http://localhost:8501>
