from flask import Flask, render_template, request, jsonify # type: ignore
import numpy as np # type: ignore
import sympy as sp # type: ignore
import os

app = Flask(__name__)

def safe_eval(expression, x_val):
    """Safely evaluate mathematical expression"""
    try:
        # Replace common mathematical functions
        expression = expression.replace('sin', 'np.sin')
        expression = expression.replace('cos', 'np.cos')
        expression = expression.replace('tan', 'np.tan')
        expression = expression.replace('exp', 'np.exp')
        expression = expression.replace('log', 'np.log')
        expression = expression.replace('sqrt', 'np.sqrt')
        expression = expression.replace('^', '**')
        
        # Create safe namespace
        namespace = {
            'x': x_val,
            'np': np,
            'pi': np.pi,
            'e': np.e
        }
        
        return eval(expression, {"__builtins__": {}}, namespace)
    except Exception as e: # Tangani error lebih spesifik
        raise ValueError(f"Ekspresi tidak valid: {expression}. Detail: {e}")

def trapesium_rule(func_str, a, b, n):
    """Calculate integral using trapezoidal rule"""
    # Pastikan n adalah integer positif
    if not isinstance(n, int) or n <= 0:
        raise ValueError("Jumlah interval (n) harus bilangan bulat positif.")
    
    h = (b - a) / n
    x_vals = np.linspace(a, b, n + 1)
    y_vals = []
    
    # Calculate function values
    for x in x_vals:
        y_vals.append(safe_eval(func_str, x))
    
    # Trapezoidal rule formula
    # result = (h / 2) * (y_vals[0] + 2 * sum(y_vals[1:-1]) + y_vals[-1]) # Versi lama
    integral_result = 0.5 * h * (y_vals[0] + 2 * np.sum(y_vals[1:n]) + y_vals[n]) # Menggunakan np.sum untuk performa

    iteration_table = []
    for i in range(len(x_vals)):
        coef = 1 # Default untuk titik awal dan akhir
        if i > 0 and i < len(x_vals) - 1:
            coef = 2 # Koefisien 2 untuk titik tengah
        
        iteration_table.append({
            'index': i,
            'x': x_vals[i],
            'fx': y_vals[i],
            'coef': coef # Menambahkan koefisien ke tabel
        })
    
    return integral_result, x_vals.tolist(), y_vals, iteration_table

def simpson_rule(func_str, a, b, n):
    """Calculate integral using Simpson's 1/3 rule"""
    # Pastikan n adalah integer genap positif
    if not isinstance(n, int) or n <= 0:
        raise ValueError("Jumlah interval (n) harus bilangan bulat positif.")
    if n % 2 != 0:
        # Jika n ganjil, naikkan atau turunkan ke bilangan genap terdekat
        n_original = n
        n = n + 1 if n % 2 != 0 else n # Contoh: jika 3 jadi 4, jika 5 jadi 6
        if n > 1000: # Batasan untuk menghindari n yang terlalu besar
            n = 1000
        # Optional: beri warning ke user bahwa n diubah
        # raise ValueError(f"Jumlah interval (n={n_original}) untuk aturan Simpson 1/3 harus genap. Silakan coba n genap.")
    
    h = (b - a) / n
    x_vals = np.linspace(a, b, n + 1)
    y_vals = []
    
    # Calculate function values
    for x in x_vals:
        y_vals.append(safe_eval(func_str, x))
    
    # Simpson's 1/3 rule formula
    integral_result = h / 3 * (y_vals[0] + 4 * np.sum(y_vals[1:n:2]) + 2 * np.sum(y_vals[2:n:2]) + y_vals[n]) # Menggunakan np.sum

    iteration_table = []
    for i in range(len(x_vals)):
        coef = 0
        if i == 0 or i == len(x_vals) - 1:
            coef = 1
        elif i % 2 == 0: # Indeks genap
            coef = 2
        else: # Indeks ganjil
            coef = 4
        iteration_table.append({
            'index': i,
            'x': x_vals[i],
            'fx': y_vals[i],
            'coef': coef
        })
    
    return integral_result, x_vals.tolist(), y_vals, iteration_table

def calculate_analytical(func_str, a, b):
    """Try to calculate analytical integral using sympy"""
    try:
        x = sp.Symbol('x')
        # Convert string to sympy expression
        # Hati-hati dengan np.sin, np.cos. Ganti kembali ke sin, cos biasa untuk SymPy
        func_str_sympy = func_str.replace('**', '^').replace('np.sin', 'sin').replace('np.cos', 'cos').replace('np.tan', 'tan').replace('np.exp', 'exp').replace('np.log', 'log').replace('np.sqrt', 'sqrt')
        expr = sp.sympify(func_str_sympy)
        
        # Calculate definite integral
        result = sp.integrate(expr, (x, a, b))
        return float(result.evalf())
    except:
        return None

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/trapesium')
def trapesium():
    return render_template('trapesium.html')

@app.route('/simpson')
def simpson():
    return render_template('simpson.html')

@app.route('/calculate_trapesium', methods=['POST'])
def calculate_trapesium():
    try:
        data = request.get_json()
        func_str = data['function']
        a = float(data['lower_bound']) # Pastikan float
        b = float(data['upper_bound']) # Pastikan float
        
        n = None
        h_val = None

        # Logic untuk menerima n_intervals atau h_value
        if 'n_intervals' in data and data['n_intervals'] is not None and data['n_intervals'] != '':
            n = int(data['n_intervals'])
        elif 'h_value' in data and data['h_value'] is not None and data['h_value'] != '':
            h_val = float(data['h_value'])
            if h_val <= 0:
                raise ValueError("Lebar interval (h) harus lebih besar dari 0.")
            n = int(round((b - a) / h_val)) # Hitung n dari h, bulatkan ke integer terdekat
            if n <= 0: # Pastikan n tidak nol atau negatif setelah pembulatan
                 raise ValueError("Jumlah interval (n) menjadi nol atau negatif. Sesuaikan h atau batas integral.")
            
        if n is None:
            raise ValueError("Harap masukkan jumlah interval (n) atau lebar interval (h).")
        
        # Calculate using trapezoidal rule
        trap_result, x_vals, y_vals, iteration_table = trapesium_rule(func_str, a, b, n)
        
        # Calculate analytical result
        analytical = calculate_analytical(func_str, a, b)
        
        # Generate more points for smooth curve visualization
        x_smooth = np.linspace(a, b, 100) # 100 titik untuk kurva halus
        y_smooth = [safe_eval(func_str, x) for x in x_smooth]
        
        return jsonify({
            'trapesium_result': trap_result,
            'analytical_result': analytical,
            'x_values': x_smooth.tolist(), # untuk grafik fungsi
            'y_values': y_smooth,         # untuk grafik fungsi
            'trapezoid_points_x': x_vals, # titik-titik untuk visualisasi trapesium
            'trapezoid_points_y': y_vals, # titik-titik untuk visualisasi trapesium
            'iteration_table': iteration_table,
            'n_used': n, # Mengembalikan nilai n yang digunakan
            'h_used': (b-a)/n # Mengembalikan nilai h yang digunakan
        })
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400 # Bad Request
    except Exception as e:
        return jsonify({'error': f"Terjadi kesalahan: {str(e)}", 'trace': str(e.__traceback__)}), 500 # Internal Server Error

@app.route('/calculate_simpson', methods=['POST'])
def calculate_simpson():
    try:
        data = request.get_json()
        func_str = data['function']
        a = float(data['lower_bound'])
        b = float(data['upper_bound'])
        
        n = None
        h_val = None

        # Logic untuk menerima n_intervals atau h_value
        if 'n_intervals' in data and data['n_intervals'] is not None and data['n_intervals'] != '':
            n = int(data['n_intervals'])
        elif 'h_value' in data and data['h_value'] is not None and data['h_value'] != '':
            h_val = float(data['h_value'])
            if h_val <= 0:
                raise ValueError("Lebar interval (h) harus lebih besar dari 0.")
            n = int(round((b - a) / h_val))
            if n <= 0:
                 raise ValueError("Jumlah interval (n) menjadi nol atau negatif. Sesuaikan h atau batas integral.")
        
        if n is None:
            raise ValueError("Harap masukkan jumlah interval (n) atau lebar interval (h).")
        
        # Untuk Simpson, n harus genap. Jika ganjil, bulatkan ke genap terdekat.
        if n % 2 != 0:
            n_original = n
            n = n + 1 # Naikkan ke genap terdekat jika ganjil
            if n > 1000: # Batas maksimum untuk n
                n = 1000
            # Optional: Anda bisa tambahkan pesan peringatan di UI jika n diubah
            # Misalnya, kirimkan 'warning_message' di JSON response
            
        # menghitung menggunakan aturan simpson
        simpson_result, x_vals, y_vals, iteration_table = simpson_rule(func_str, a, b, n)
        
        # menghitung hasil secara analitik...
        analytical = calculate_analytical(func_str, a, b)
        
        # Generate lebih banyak titik untuk membuat kurva lebih halus
        x_smooth = np.linspace(a, b, 100)
        y_smooth = [safe_eval(func_str, x) for x in x_smooth]
        
        return jsonify({
            'simpson_result': simpson_result,
            'analytical_result': analytical,
            'x_values': x_smooth.tolist(),
            'y_values': y_smooth,
            'simpson_points_x': x_vals, # titik-titik untuk visualisasi simpson
            'simpson_points_y': y_vals, # titik-titik untuk visualisasi simpson
            'iteration_table': iteration_table,
            'n_used': n, # Mengembalikan nilai n yang digunakan
            'h_used': (b-a)/n # Mengembalikan nilai h yang digunakan
        })
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f"Terjadi kesalahan: {str(e)}", 'trace': str(e.__traceback__)}), 500

if __name__ == '__main__':
    print("=== KALKULATOR INTEGRAL NUMERIK ===")
    print("Website telah siap dengan fitur:")
    print("✅ Halaman Home untuk memilih metode")
    print("✅ Metode Trapesium dengan visualisasi")
    print("✅ Metode Simpson 1/3 dengan visualisasi")
    print("✅ Perhitungan galat absolut dan relatif")
    print("✅ Grafik interaktif menggunakan Chart.js")
    print("✅ Interface responsif dengan Bootstrap")
    print("\nCara menjalankan:")
    print("1. Install dependencies: pip install flask numpy sympy")
    print("2. Jalankan: python app.py")
    print("3. Buka browser: http://localhost:5000")
    
    # app.run(debug=True) # Dalam produksi, set debug=False atau gunakan gunicorn/lainnya
    app.run(debug=True, host='0.0.0.0') # Agar bisa diakses dari perangkat lain di jaringan lokal