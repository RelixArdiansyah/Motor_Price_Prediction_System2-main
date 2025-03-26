# Motor_Price_Prediction_System

This is an end-to-end Motor Price Prediction System, developed using Linear Regression for machine learning and Flask for the backend. The frontend is built with HTML, CSS, and JavaScript, while MySQL is used for data storage and management. The system provides accurate motor price estimates based on user input and historical data.

## Features
- **User Input:** Users can enter motor specifications such as year, kilometers driven, company, and model.
- **Price Prediction:** Utilizes multiple linear regression to estimate the price of the motor.
- **Historical Data:** Predictions are based on a dataset extracted from OLX.
- **Real Price Display:** The system shows both the predicted price and the actual market price.
- **Persistent Input Fields:** User input remains in the form after prediction for ease of comparison.
- **Dark Mode Support:** Users can toggle between light and dark mode.

## Technologies Used
- **Machine Learning:** Linear Regression (SPSS for model validation)
- **Backend:** Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL
- **Testing:** Blackbox Testing, Excel Data Validation

## Web Page
![website](images/prediksi.png)

## Accuracy
![accuracy](images/akurasi.png)

## Installation Guide
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Motor_Price_Prediction_System.git
   cd Motor_Price_Prediction_System
   ```
2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
3. **Set up the database:**
   - Import `database.sql` into MySQL.
   - Update database credentials in `config.py`.
4. **Run the application:**
   ```bash
   python app.py
   ```
5. **Access the application:**
   Open `http://127.0.0.1:5000/` in your browser.

## Future Improvements
- Enhancing the prediction model with more features.
- Adding user authentication for personalized experience.
- Implementing REST API for external integrations.

## License
This project is open-source under the MIT License.
![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)
