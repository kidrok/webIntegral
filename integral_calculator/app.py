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
    except:
        raise ValueError(f"Invalid expression: {expression}")

def trapesium_rule(func_str, a, b, n):
    """Calculate integral using trapezoidal rule"""
    h = (b - a) / n
    x_vals = np.linspace(a, b, n + 1)
    y_vals = []
    
    # Calculate function values
    for x in x_vals:
        y_vals.append(safe_eval(func_str, x))
    
    # Trapezoidal rule
    result = (h / 2) * (y_vals[0] + 2 * sum(y_vals[1:-1]) + y_vals[-1])
    
    return result, x_vals, y_vals

def simpson_rule(func_str, a, b, n):
    """Calculate integral using Simpson's 1/3 rule"""
    if n % 2 != 0:
        raise ValueError("Number of intervals must be even for Simpson's rule")
    
    h = (b - a) / n
    x_vals = np.linspace(a, b, n + 1)
    y_vals = []
    
    # Calculate function values
    for x in x_vals:
        y_vals.append(safe_eval(func_str, x))
    
    # Simpson's 1/3 rule
    result = h / 3 * (y_vals[0] + 4 * sum(y_vals[1:-1:2]) + 2 * sum(y_vals[2:-1:2]) + y_vals[-1])
    
    return result, x_vals, y_vals

def calculate_analytical(func_str, a, b):
    """Try to calculate analytical integral using sympy"""
    try:
        x = sp.Symbol('x')
        # Convert string to sympy expression
        func_str_sympy = func_str.replace('**', '^').replace('np.', '')
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
        a = data['lower_bound']
        b = data['upper_bound']
        n = data['n_intervals']
        
        # Calculate using trapezoidal rule
        trap_result, x_vals, y_vals = trapesium_rule(func_str, a, b, n)
        
        # Calculate analytical result
        analytical = calculate_analytical(func_str, a, b)
        
        # Generate more points for smooth curve visualization
        x_smooth = np.linspace(a, b, 100)
        y_smooth = [safe_eval(func_str, x) for x in x_smooth]
        
        iteration_table = []
        for i in range(len(x_vals)):
            if i == 0 or i == len(x_vals) - 1:
                coef = 1
            elif i % 2 == 0:
                coef = 2
            else:
                coef = 4
            iteration_table.append({
                'index': i,
                'x': x_vals[i],
                'fx': y_vals[i],
                'coef': coef
            })


        return jsonify({
            'trapesium_result': trap_result,
            'analytical_result': analytical,
            'x_values': x_smooth.tolist(),
            'y_values': y_smooth,
            'trapezoid_points': y_vals,
            'iteration_table': iteration_table
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/calculate_simpson', methods=['POST'])
def calculate_simpson():
    try:
        data = request.get_json()
        func_str = data['function']
        a = data['lower_bound']
        b = data['upper_bound']
        n = data['n_intervals']
        
        # menghitung menggunakan aturan simpson
        simpson_result, x_vals, y_vals = simpson_rule(func_str, a, b, n)
        
        # menghitung hasil secara analitik...
        analytical = calculate_analytical(func_str, a, b)
        
        # Generate lebih banyak titik untuk membuat kurva lebih halus
        x_smooth = np.linspace(a, b, 100)
        y_smooth = [safe_eval(func_str, x) for x in x_smooth]
        
        iteration_table = []
        for i in range(len(x_vals)):
            if i == 0 or i == len(x_vals) - 1:
                coef = 1
            elif i % 2 == 0:
                coef = 2
            else:
                coef = 4
            iteration_table.append({
                'index': i,
                'x': x_vals[i],
                'fx': y_vals[i],
                'coef': coef
            })


        return jsonify({
            'simpson_result': simpson_result,
            'analytical_result': analytical,
            'x_values': x_smooth.tolist(),
            'y_values': y_smooth,
            'simpson_points': y_vals,
            'iteration_table': iteration_table
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

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
    print("1. Install dependencies: pip install flask numpy matplotlib sympy")
    print("2. Jalankan: python app.py")
    print("3. Buka browser: http://localhost:5000")
    
    app.run(debug=True)