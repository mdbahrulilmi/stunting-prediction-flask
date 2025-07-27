from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from datetime import datetime
from src.db import fetch_dataset_pengukuran
import numpy as np

_knn_model = None
_scaler = None

MONTH_MAP = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MEI": 5, "JUN": 6,
    "JUL": 7, "AGS": 8, "SEP": 9, "OKT": 10, "NOV": 11, "DES": 12
}

def parse_bulan(bulan_str):
    try:
        year_str, month_abbr = bulan_str.split("_")
        bulan = MONTH_MAP.get(month_abbr.upper(), 1)
        tahun = int(year_str)
        return datetime(tahun, bulan, 15)
    except:
        return datetime.min

def hitung_umur_bulan(tgl_lahir_str, bulan_pemeriksaan_str):
    try:
        tgl_lahir = datetime.strptime(tgl_lahir_str, "%d/%m/%Y")
        tgl_pemeriksaan = parse_bulan(bulan_pemeriksaan_str)
        umur = (tgl_pemeriksaan.year - tgl_lahir.year) * 12 + (tgl_pemeriksaan.month - tgl_lahir.month)
        return max(umur, 0)
    except Exception as e:
        print(f"❌ Error hitung umur: {e}")
        return None

def ambil_data_terakhir_per_balita(dataset):
    latest = {}
    for row in dataset:
        key = row.get("tgl_lahir") + "_" + row.get("jenis_kelamin")
        current = latest.get(key)
        this_date = parse_bulan(row.get("bulan"))
        if current is None or this_date > parse_bulan(current.get("bulan")):
            latest[key] = row
    return list(latest.values())

def load_knn_model():
    global _knn_model, _scaler
    if _knn_model is not None:
        return _knn_model

    dataset = fetch_dataset_pengukuran()
    if not dataset or len(dataset) < 3:
        print("Dataset tidak cukup")
        return None

    dataset = ambil_data_terakhir_per_balita(dataset)
    X, y = [], []
    dilewati = 0

    for row in dataset:
        umur = hitung_umur_bulan(row.get("tgl_lahir"), row.get("bulan"))
        if umur is None:
            dilewati += 1
            continue

        try:
            berat = float(str(row['berat']).replace(',', '.'))
            tinggi = float(str(row['tinggi']).replace(',', '.'))
            status = row['status'].strip().lower()
            jk = row.get('jenis_kelamin', '').strip().upper()

            if status not in ['stunting', 'tidak stunting'] or jk not in ['L', 'P']:
                dilewati += 1
                continue

            gender = 1 if jk == 'L' else 0
            bb_per_tb = berat / tinggi if tinggi else 0
            bb_per_umur = berat / umur if umur else 0
            bmi = berat / ((tinggi / 100) ** 2)

            fitur = [umur, berat, tinggi, gender, bb_per_tb, bb_per_umur, bmi]
            X.append(fitur)
            y.append(status)
        except:
            dilewati += 1
            continue

    if len(X) < 3:
        print("Data latih tidak cukup")
        return None

    print("Distribusi awal status gizi:")
    for label, count in Counter(y).items():
        print(f"- {label}: {count} data")
    print(f"🔍 Data dilewati: {dilewati}")

    # Encode label
    y_encoded = [1 if label == "stunting" else 0 for label in y]

    # Normalisasi
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ➕ SMOTE untuk seimbangkan
    sm = SMOTE(random_state=42)
    X_res, y_res = sm.fit_resample(X_scaled, y_encoded)

    print(f"📈 Data setelah SMOTE:")
    print(f"- tidak stunting: {list(y_res).count(0)}")
    print(f"- stunting: {list(y_res).count(1)}")

    X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)

    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    _knn_model = model
    _scaler = scaler
    return model

def predict_gizi_status(umur, berat, tinggi, gender):
    global _scaler
    model = load_knn_model()
    if model is None or umur is None or _scaler is None:
        print("⚠️ Model belum tersedia atau umur tidak valid.")
        return "Tidak cukup data"

    try:
        jk = 1 if gender.upper() == 'L' else 0
        bb_per_tb = berat / tinggi if tinggi else 0
        bb_per_umur = berat / umur if umur else 0
        bmi = berat / ((tinggi / 100) ** 2)

        fitur = [[umur, berat, tinggi, jk, bb_per_tb, bb_per_umur, bmi]]
        fitur_scaled = _scaler.transform(fitur)
        pred = model.predict(fitur_scaled)[0]

        label = "stunting" if pred == 1 else "tidak stunting"

        return label

    except Exception as e:
        print(f"❌ Error saat prediksi: {e}")
        return "Gagal prediks"
