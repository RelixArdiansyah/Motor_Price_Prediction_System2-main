from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pandas as pd
import pickle
import os
import json
from flask_bcrypt import Bcrypt
import mysql.connector
from mysql.connector import Error
import subprocess
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import io
import base64

# Inisialisasi aplikasi Flask
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'your_secret_key_here'

# Memuat data motor yang telah dibersihkan
motor = pd.read_csv("olx_cleaned2.csv")
motor.columns = motor.columns.str.lower()  # Mengubah semua nama kolom menjadi huruf kecil

# Memuat mapping dari file JSON
with open('mappings.json', 'r') as f:
    mappings = json.load(f)

# Fungsi untuk mengembalikan nama asli dari encoding
def decode_value(column, value):
    reverse_mapping = {v: k for k, v in mappings[column].items()}
    return reverse_mapping.get(value, value)

# Fungsi untuk mengubah nama asli ke angka (encoding)
def encode_value(column, value):
    return mappings[column].get(value, None)

# Fungsi untuk membuat tabel users jika belum ada
def create_user_table():  
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="admin123",
            database="prediksi_motor"
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                username VARCHAR(50) PRIMARY KEY,
                                password VARCHAR(255) NOT NULL)''')
            conn.commit()
            cursor.close()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# Fungsi untuk menambahkan pengguna ke database
def add_user(username, password):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="admin123",
            database="prediksi_motor"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# Fungsi untuk memeriksa kredensial pengguna di database
def check_user(username, password):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="admin",
            password="admin123",
            database="prediksi_motor"
        )      
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result and bcrypt.check_password_hash(result[0], password):
            return True
        return False
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# Membuat tabel users jika belum ada
create_user_table()

# Rute untuk halaman Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="admin",
                password="admin123",
                database="prediksi_motor"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_exists = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_exists:
                flash('Username sudah terdaftar, silakan pilih username lain.', 'danger')
                return redirect(url_for('register'))
            
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            add_user(username, hashed_password)
            
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        
        except Error as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('register.html')

# Rute untuk halaman Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if check_user(username, password):
            session['username'] = username
            flash('Login berhasil!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah.', 'danger')
    
    return render_template('login.html')

@app.route('/get_motor_models/<company>', methods=['GET'])
def get_motor_models(company):
    try:
        models = sorted(motor[motor['company'] == company]['name'].unique())
        return jsonify(models)
    except Exception as e:
        print(f"Error fetching motor models: {e}")
        return jsonify([])

@app.route('/', methods=['GET', 'POST'])
def index():
    companies = sorted(motor['company'].unique())
    fuel_types = sorted(motor['fuel_type'].unique())
    years = sorted(motor['year'].unique(), reverse=True)

    prediction = None
    r_squared = None
    intercept = None
    graph_url = None  # Untuk menyimpan grafik harga motor

    selected_company = request.form.get('company')
    selected_name = request.form.get('motor_name')
    selected_fuel = request.form.get('fuel')

    if request.method == 'POST':
        try:
            selected_year = int(request.form.get('year'))
            selected_kilo = int(request.form.get('kilo'))

            filename = f"file_pkl/MotorPriceModel_{selected_company}_{selected_name}_{selected_fuel}.pkl"
            
            if not os.path.exists(filename):
                flash('Model tidak tersedia untuk kombinasi tersebut.', 'danger')
            else:
                with open(filename, 'rb') as file:
                    model_data = pickle.load(file)

                model = model_data['model']
                r_squared = model_data.get('r_squared', None)
                intercept = model_data.get('intercept', None)
                
                input_data = pd.DataFrame([[selected_year, selected_kilo, 
                                            encode_value('company', selected_company), 
                                            encode_value('name', selected_name), 
                                            encode_value('fuel_type', selected_fuel)]],
                                          columns=['year', 'kms_driven', 'company', 'name', 'fuel_type'])
                prediction = model.predict(input_data)[0]
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    # **Membuat Grafik Berdasarkan Pilihan Pengguna**
    if selected_company and selected_name:
        filtered_data = motor[(motor['company'] == selected_company) & (motor['name'] == selected_name)]
        
        if not filtered_data.empty:
            plt.figure(figsize=(8, 5))
            sns.lineplot(data=filtered_data, x="year", y="price", marker="o", color="orange")
            plt.xlabel("Tahun")
            plt.ylabel("Harga (Juta Rp)")
            plt.title(f"Tren Harga Motor {selected_name} ({selected_company})")

            # Format sumbu Y ke dalam juta (contoh: 12.560.000 → 12.6)
            plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x/1_000_000:.1f}'))

            # Simpan gambar sebagai Base64
            img = io.BytesIO()
            plt.savefig(img, format="png", bbox_inches="tight")
            img.seek(0)
            graph_url = base64.b64encode(img.getvalue()).decode()
            plt.close()  # Hindari memory leak

    return render_template('index.html', companies=companies, fuel_types=fuel_types, years=years, 
                           prediction=prediction, r_squared=r_squared, intercept=intercept,
                           graph_url=graph_url)



@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Anda berhasil logout.', 'success')
    return redirect(url_for('login'))

@app.route('/crud', methods=['GET', 'POST'])
def crud():
    if 'username' not in session:
        flash('Silakan login terlebih dahulu.', 'danger')
        return redirect(url_for('login'))
    
    csv_file_path = "olx.csv"
    motor_data = pd.read_csv(csv_file_path)
    motor_data.columns = motor_data.columns.str.lower()

    def save_data(data):
        data.to_csv(csv_file_path, index=False)

    if request.method == 'POST':
        action = request.form.get('action')

        try:
            if action == 'add':
                new_data = {
                    'company': request.form['company'],
                    'name': request.form['name'],
                    'year': int(request.form['year']),
                    'kms_driven': int(request.form['kms_driven']),
                    'fuel_type': request.form['fuel_type'],
                    'price': int(request.form['price']),
                }
                motor_data = pd.concat([motor_data, pd.DataFrame([new_data])], ignore_index=True)
                save_data(motor_data)
                flash('Data berhasil ditambahkan.', 'success')

            elif action == 'delete':
                row_id = int(request.form['row_id'])
                motor_data.drop(index=row_id, inplace=True)
                motor_data.reset_index(drop=True, inplace=True)
                save_data(motor_data)
                flash('Data berhasil dihapus.', 'success')


        except Exception as e:
            flash(f'Error dalam operasi: {str(e)}', 'danger')
    
    # Handle search
    search_query = request.args.get('search', '').lower()
    if search_query:
        motor_data = motor_data[motor_data.apply(lambda row: search_query in row.to_string().lower(), axis=1)]

    return render_template('crud.html', motor_data=motor_data.to_dict(orient='records'))

@app.route('/run_script', methods=['POST'])
def run_script():
    try:
        # Tentukan jalur lengkap ke script Python
        script_path = os.path.abspath("PrediksiHargaMotorJadi2.py")
        # Jalankan script menggunakan Python
        subprocess.run(['python', script_path], check=True)
        flash('Script berhasil dijalankan.', 'success')
    except subprocess.CalledProcessError:
        flash('Gagal menjalankan script: Error dalam proses eksekusi.', 'danger')
    except Exception as e:
        flash(f'Gagal menjalankan script: {str(e)}', 'danger')
    return redirect(url_for('crud'))

print(os.path.abspath("PrediksiHargaMotorJadi2.py"))


if __name__ == '__main__':
    app.run(debug=True)
