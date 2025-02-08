import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
import os
import shutil
import json  # Untuk menyimpan dan membaca mapping

motor= pd.read_csv('olx.csv')

motor['year'] = motor['year'].astype(int)

motor.info

# Pastikan harga diformat dengan benar dan hapus '.0' jika ada
motor['price'] = motor['price'].astype(str)  # Pastikan tipe data string
motor['price'] = motor['price'].str.replace('.', '', regex=False)  # Hapus semua titik
motor['price'] = motor['price'].str.replace(',', '', regex=False)  # Hapus semua koma
motor['price'] = motor['price'].astype(int).astype(str)  # Konversi ke integer


motor['kms_driven'] = motor['kms_driven'].str.split(" ").str.get(0).str.replace(',', '')
motor = motor[motor['kms_driven'].str.isnumeric()]
motor['kms_driven'] = motor['kms_driven'].astype(int)

motor = motor[~motor['fuel_type'].isna()]

columns_to_encode = ['company', 'name', 'fuel_type']
mappings = {}

for col in columns_to_encode:
    mappings[col] = {k: i for i, k in enumerate(motor[col].value_counts().index, 1)}
    motor[col] = motor[col].map(mappings[col])

with open('mappings.json', 'w') as f:
    json.dump(mappings, f)

motor.to_csv('olx_cleaned.csv', index=False)

if not os.path.exists('file_pkl'):
    os.makedirs('file_pkl')

def train_model(company, motor_model, fuel_type):
    # Filter data untuk kombinasi tertentu
    filtered_motor = motor[
        (motor['company'] == company) & 
        (motor['name'] == motor_model) & 
        (motor['fuel_type'] == fuel_type)
    ]

    # Pastikan data cukup untuk melatih model
    if len(filtered_motor) < 2:
        print(f"Not enough data for company: {company}, model: {motor_model}, fuel: {fuel_type}")
        return None

    # Define fitur dan target
    X = filtered_motor[['year', 'kms_driven', 'company', 'name', 'fuel_type']]
    y = filtered_motor['price']

    # Melatih model
    model = LinearRegression()
    model.fit(X, y)

    # Mendapatkan nama asli dari encoding
    company_name = [k for k, v in mappings['company'].items() if v == company][0]
    model_name = [k for k, v in mappings['name'].items() if v == motor_model][0]
    fuel_name = [k for k, v in mappings['fuel_type'].items() if v == fuel_type][0]

    # Menyimpan model
    filename = f"MotorPriceModel_{company_name}_{model_name}_{fuel_name}.pkl"
    pickle.dump(model, open(filename, 'wb'))
    shutil.move(filename, os.path.join('file_pkl', filename))
    print(f"Model saved: file_pkl/{filename}")
    return filename

for company in motor['company'].unique():
    for motor_model in motor[motor['company'] == company]['name'].unique():
        for fuel_type in motor[
            (motor['company'] == company) & (motor['name'] == motor_model)
        ]['fuel_type'].unique():
            train_model(company, motor_model, fuel_type)

with open('mappings.json', 'r') as f:
    mappings = json.load(f)

for col in columns_to_encode:
    reverse_mapping = {v: k for k, v in mappings[col].items()}
    motor[col] = motor[col].map(reverse_mapping)

motor.to_csv('olx_cleaned2.csv', index=False)

print("Proses selesai.")

