from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from datetime import datetime
from src.db import fetch_dataset_pengukuran

_knn_model = None

MONTH_MAP = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MEI": 5, "JUN": 6,
    "JUL": 7, "AGS": 8, "SEP": 9, "OKT": 10, "NOV": 11, "DES": 12
}

def hitung_umur_bulan(tgl_lahir_str, bulan_pemeriksaan_str):
    try:
        tgl_lahir = datetime.strptime(tgl_lahir_str, "%d/%m/%Y")
        year_str, month_abbr = bulan_pemeriksaan_str.split("_")
        bulan = MONTH_MAP.get(month_abbr.upper(), 1)
        tahun = int(year_str)
        tanggal_pemeriksaan = datetime(tahun, bulan, 15)
        umur = (tanggal_pemeriksaan.year - tgl_lahir.year) * 12 + (tanggal_pemeriksaan.month - tgl_lahir.month)
        return umur
    except Exception as e:
        print(f"Error hitung umur: {e}")
        return None

def load_knn_model():
    global _knn_model
    if _knn_model is not None:
        return _knn_model

    dataset = fetch_dataset_pengukuran()
    if not dataset or len(dataset) < 3:
        print("Dataset tidak cukup")
        return None

    X = []
    y = []
    data_dilewati = 0

    for row in dataset:
        umur = hitung_umur_bulan(row.get("tgl_lahir"), row.get("bulan"))
        if umur is None:
            data_dilewati += 1
            continue

        try:
            berat = float(row['berat'])
            tinggi = float(row['tinggi'])
            status = row['status'].strip().lower()
            jk = row.get('jenis_kelamin', '').strip().upper()

            if status not in ['stunting', 'tidak stunting']:
                data_dilewati += 1
                continue

            if jk not in ['L', 'P']:
                data_dilewati += 1
                continue

            gender = 1 if jk == 'L' else 0

            bb_per_tb = berat / tinggi
            bb_per_umur = berat / umur

            fitur = [umur, berat, tinggi, gender, bb_per_tb, bb_per_umur]
            X.append(fitur)
            y.append(status)
        except Exception as e:
            data_dilewati += 1
            continue

    if len(X) < 3:
        print("Data latih tidak cukup")
        return None

    label_counter = Counter(y)
    print("Distribusi label status gizi (data latih):")
    for label, count in label_counter.items():
        print(f"- {label}: {count} data")

    print(f"🔍 Data yang dilewati: {data_dilewati}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n✅ Akurasi model (validasi 20%): {acc:.2%}\n")

    _knn_model = model
    return model

def predict_gizi_status(umur, berat, tinggi, gender):
    model = load_knn_model()
    if model is None or umur is None:
        print("⚠️ Model belum tersedia atau umur tidak valid.")
        return "Tidak cukup data"

    try:
        jk = 1 if gender.upper() == 'L' else 0

        # Hindari pembagian dengan nol
        bb_per_tb = berat / tinggi if tinggi != 0 else 0
        bb_per_umur = berat / umur if umur != 0 else 0  # kasih 0 kalau umur 0

        fitur = [[umur, berat, tinggi, jk, bb_per_tb, bb_per_umur]]
        pred = model.predict(fitur)[0]

        print("\n=== Hasil Prediksi Pemeriksaan ===")
        print(f"📅 Umur (bulan): {umur}")
        print(f"⚖️ Berat badan: {berat} kg")
        print(f"📏 Tinggi badan: {tinggi} cm")
        print(f"👶 Jenis Kelamin: {gender}")
        print(f"✅ Status gizi diprediksi: {pred}")
        print("==================================\n")

        return pred

    except Exception as e:
        print(f"❌ Error saat prediksi: {e}")
        return "Gagal prediksi"
