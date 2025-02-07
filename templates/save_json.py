import json

# Data yang digabungkan
data = {
    "companies": [
        {
            "company_id": 1,
            "company_name": "Company A"
        },
        {
            "company_id": 2,
            "company_name": "Company B"
        }
    ],
    "models": [
        {
            "model_id": 1,
            "company_id": 1,
            "model_name": "Model X"
        },
        {
            "model_id": 2,
            "company_id": 1,
            "model_name": "Model Y"
        },
        {
            "model_id": 3,
            "company_id": 2,
            "model_name": "Model Z"
        }
    ],
    "motors": [
        {
            "id": 1,
            "company": 1,
            "name": 1,
            "year": 2022,
            "kms_driven": 10000,
            "Price": 15000000,
            "fuel_type": "Petrol"
        },
        {
            "id": 2,
            "company": 1,
            "name": 2,
            "year": 2021,
            "kms_driven": 20000,
            "Price": 12000000,
            "fuel_type": "Diesel"
        },
        {
            "id": 3,
            "company": 2,
            "name": 3,
            "year": 2023,
            "kms_driven": 5000,
            "Price": 20000000,
            "fuel_type": "Electric"
        }
    ],
    "predictions": [
        {
            "prediction_id": 1,
            "company_id": 1,
            "model_id": 1,
            "year": 2022,
            "kms_driven": 10000,
            "predicted_price": 15500000
        },
        {
            "prediction_id": 2,
            "company_id": 1,
            "model_id": 2,
            "year": 2021,
            "kms_driven": 20000,
            "predicted_price": 12500000
        },
        {
            "prediction_id": 3,
            "company_id": 2,
            "model_id": 3,
            "year": 2023,
            "kms_driven": 5000,
            "predicted_price": 21000000
        }
    ]
}

# Fungsi untuk menyimpan data ke file JSON
def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Menyimpan data ke satu file JSON
save_to_json(data, 'combined_data.json')

print("File JSON telah disimpan.")
