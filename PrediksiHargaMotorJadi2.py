import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
import os
import shutil
import json  # Untuk menyimpan dan membaca mapping

# Membaca dataset
motor = pd.read_csv('olx.csv')

# Konversi kolom ke tipe data yang sesuai
motor['year'] = motor['year'].astype(int)
motor['price'] = motor['price'].astype(str).str.replace('.', '', regex=False).str.replace(',', '', regex=False).astype(int)
motor['kms_driven'] = motor['kms_driven'].str.split(" ").str.get(0).str.replace(',', '')
motor = motor[motor['kms_driven'].str.isnumeric()]
motor['kms_driven'] = motor['kms_driven'].astype(int)

# Menghapus data yang tidak memiliki fuel_type
motor = motor[~motor['fuel_type'].isna()]

# Encoding kolom kategori
columns_to_encode = ['company', 'name', 'fuel_type']
mappings = {}

for col in columns_to_encode:
    mappings[col] = {k: i for i, k in enumerate(motor[col].value_counts().index, 1)}
    motor[col] = motor[col].map(mappings[col])

# Menyimpan mapping untuk decoding
with open('mappings.json', 'w') as f:
    json.dump(mappings, f)

# Simpan dataset setelah encoding
motor.to_csv('olx_cleaned.csv', index=False)

# Membuat folder penyimpanan model jika belum ada
if not os.path.exists('file_pkl'):
    os.makedirs('file_pkl')

# Fungsi untuk melatih model dan menyimpan hasil regresi
def train_model(company, motor_model, fuel_type):
    # Filter data untuk kombinasi tertentu
    filtered_motor = motor[
        (motor['company'] == company) & 
        (motor['name'] == motor_model) & 
        (motor['fuel_type'] == fuel_type)
    ]

    # Pastikan ada cukup data untuk melatih model
    if len(filtered_motor) < 2:
        print(f"Not enough data for company: {company}, model: {motor_model}, fuel: {fuel_type}")
        return None

    # Definisi fitur dan target
    X = filtered_motor[['year', 'kms_driven', 'company', 'name', 'fuel_type']]
    y = filtered_motor['price']

    # Melatih model regresi linear
    model = LinearRegression()
    model.fit(X, y)

    # Menghitung nilai R² (koefisien determinasi)
    r_squared = model.score(X, y)
    intercept = model.intercept_
    
    print(f"Model trained: {company}, {motor_model}, {fuel_type}")
    print(f"R² Score: {r_squared:.4f}, Intercept: {intercept:.2f}")

    # Mendapatkan nama asli dari encoding
    company_name = [k for k, v in mappings['company'].items() if v == company][0]
    model_name = [k for k, v in mappings['name'].items() if v == motor_model][0]
    fuel_name = [k for k, v in mappings['fuel_type'].items() if v == fuel_type][0]

    # Menyimpan model, nilai R², dan intercept
    model_data = {
        'model': model,
        'r_squared': r_squared,
        'intercept': intercept
    }
    
    filename = f"MotorPriceModel_{company_name}_{model_name}_{fuel_name}.pkl"
    with open(filename, 'wb') as f:
        pickle.dump(model_data, f)
    
    shutil.move(filename, os.path.join('file_pkl', filename))
    print(f"Model saved: file_pkl/{filename}")

    return filename

# Melatih model untuk setiap kombinasi unik dari company, name, dan fuel_type
for company in motor['company'].unique():
    for motor_model in motor[motor['company'] == company]['name'].unique():
        for fuel_type in motor[(motor['company'] == company) & (motor['name'] == motor_model)]['fuel_type'].unique():
            train_model(company, motor_model, fuel_type)

# Mengembalikan data ke nama aslinya
with open('mappings.json', 'r') as f:
    mappings = json.load(f)

for col in columns_to_encode:
    reverse_mapping = {v: k for k, v in mappings[col].items()}
    motor[col] = motor[col].map(reverse_mapping)

# Simpan dataset yang telah dikembalikan ke nama aslinya
motor.to_csv('olx_cleaned2.csv', index=False)

print("Proses selesai.")
