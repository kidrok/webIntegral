from flask import Flask, render_template, request, jsonify
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sympy as sp
from io import BytesIO
import base64
import os

app = Flask(__name__)

def create_templates():
    """Membuat folder templates dan file HTML"""
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Base template
    base_template = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Kalkulator Integral Numerik{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
            }
        };
    </script>
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .btn-primary { background: linear-gradient(45deg, #667eea, #764ba2); border: none; }
        .btn-primary:hover { background: linear-gradient(45deg, #764ba2, #667eea); }
        .navbar { background: rgba(255,255,255,0.1) !important; backdrop-filter: blur(10px); }
        .result-card { background: rgba(255,255,255,0.95); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">🧮 Kalkulator Integral</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Home</a>
                <a class="nav-link" href="/trapesium">Trapesium</a>
                <a class="nav-link" href="/simpson">Simpson 1/3</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    """
    
    # Home page
    home_template = """
{% extends "base.html" %}
{% block title %}Home - Kalkulator Integral Numerik{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body text-center p-5">
                <h1 class="card-title mb-4 text-primary">
                    <i class="fas fa-calculator"></i> Kalkulator Integral Numerik
                </h1>
                <p class="card-text fs-5 mb-5">
                    Hitung integral definit menggunakan metode numerik dengan visualisasi grafik dan analisis galat
                </p>
                
                <div class="row g-4">
                    <div class="col-md-6">
                        <div class="card h-100 border-primary">
                            <div class="card-body">
                                <h3 class="text-primary mb-3">📊 Metode Trapesium</h3>
                                <p class="card-text">
                                    Approximasi integral menggunakan trapesium untuk menghitung luas area di bawah kurva
                                </p>
                                <div class="mb-3">
                                    <small class="text-muted">Formula:</small><br>
                                    <span class="badge bg-light text-dark">$$\\int_a^b f(x)dx \\approx \\frac{h}{2}[f(a) + 2\\sum_{i=1}^{n-1}f(x_i) + f(b)]$$</span>
                                </div>
                                <a href="/trapesium" class="btn btn-primary btn-lg w-100">
                                    Mulai Hitung <i class="fas fa-arrow-right"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="card h-100 border-success">
                            <div class="card-body">
                                <h3 class="text-success mb-3">📈 Metode Simpson 1/3</h3>
                                <p class="card-text">
                                    Approximasi integral menggunakan parabola untuk hasil yang lebih akurat
                                </p>
                                <div class="mb-3">
                                    <small class="text-muted">Formula:</small><br>
                                    <span class="badge bg-light text-dark">$$\\int_a^b f(x)dx \\approx \\frac{h}{3}[f(a) + 4\\sum_{odd}f(x_i) + 2\\sum_{even}f(x_i) + f(b)]$$</span>
                                </div>
                                <a href="/simpson" class="btn btn-success btn-lg w-100">
                                    Mulai Hitung <i class="fas fa-arrow-right"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-5">
                    <div class="alert alert-info">
                        <h5><i class="fas fa-info-circle"></i> Fitur yang Tersedia:</h5>
                        <ul class="list-unstyled mb-0">
                            <li>✅ Perhitungan integral numerik otomatis</li>
                            <li>✅ Perbandingan dengan nilai analitik</li>
                            <li>✅ Analisis galat absolut dan relatif</li>
                            <li>✅ Visualisasi grafik interaktif</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
    """
    
    # Trapesium page
    trapesium_template = """
{% extends "base.html" %}
{% block title %}Metode Trapesium - Kalkulator Integral{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h3 class="mb-0">📊 Metode Trapesium</h3>
            </div>
            <div class="card-body">
                <form id="trapesiumForm">
                    <div class="mb-3">
                        <label class="form-label">Fungsi f(x):</label>
                        <input type="text" class="form-control" id="function" value="x**2" placeholder="Contoh: x**2, sin(x), exp(x)">
                        <small class="form-text text-muted">Gunakan sintaks Python: x**2, sin(x), cos(x), exp(x), log(x)</small>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Batas Bawah (a):</label>
                                <input type="number" class="form-control" id="lower_bound" value="0" step="0.1">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Batas Atas (b):</label>
                                <input type="number" class="form-control" id="upper_bound" value="2" step="0.1">
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Jumlah Subinterval (n):</label>
                        <input type="number" class="form-control" id="n_intervals" value="10" min="2" step="2">
                        <small class="form-text text-muted">Harus genap untuk perbandingan dengan Simpson</small>
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100 btn-lg">
                        <i class="fas fa-calculator"></i> Hitung Integral
                    </button>
                </form>
                
                <div class="mt-4">
                    <h5>Formula Trapesium:</h5>
                    <div class="alert alert-light">
                        $$I \\approx \\frac{h}{2}[f(a) + 2\\sum_{i=1}^{n-1}f(x_i) + f(b)]$$
                        <br><small>dimana $h = \\frac{b-a}{n}$</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card result-card" id="resultCard" style="display: none;">
            <div class="card-header bg-success text-white">
                <h4 class="mb-0">📊 Hasil Perhitungan</h4>
            </div>
            <div class="card-body">
                <div id="results"></div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card" id="chartCard" style="display: none;">
            <div class="card-header">
                <h4>📈 Visualisasi Grafik</h4>
            </div>
            <div class="card-body">
                <div id="chart-container">
                    <canvas id="functionChart" width="800" height="400"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('trapesiumForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        function: document.getElementById('function').value,
        lower_bound: parseFloat(document.getElementById('lower_bound').value),
        upper_bound: parseFloat(document.getElementById('upper_bound').value),
        n_intervals: parseInt(document.getElementById('n_intervals').value)
    };
    
    fetch('/calculate_trapesium', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Show results
        document.getElementById('resultCard').style.display = 'block';
        document.getElementById('results').innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="alert alert-primary">
                        <h6>Hasil Trapesium:</h6>
                        <strong>${data.trapesium_result.toFixed(6)}</strong>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="alert alert-info">
                        <h6>Nilai Analitik:</h6>
                        <strong>${data.analytical_result ? data.analytical_result.toFixed(6) : 'Tidak tersedia'}</strong>
                    </div>
                </div>
            </div>
            ${data.analytical_result ? `
            <div class="row">
                <div class="col-md-6">
                    <div class="alert alert-warning">
                        <h6>Galat Absolut:</h6>
                        <strong>${Math.abs(data.trapesium_result - data.analytical_result).toFixed(6)}</strong>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="alert alert-danger">
                        <h6>Galat Relatif:</h6>
                        <strong>${(Math.abs(data.trapesium_result - data.analytical_result) / Math.abs(data.analytical_result) * 100).toFixed(4)}%</strong>
                    </div>
                </div>
            </div>
            ` : ''}
            <div class="alert alert-secondary">
                <small><strong>Parameter:</strong> h = ${((formData.upper_bound - formData.lower_bound) / formData.n_intervals).toFixed(4)}, n = ${formData.n_intervals}</small>
            </div>
        `;
        
        // Show chart
        document.getElementById('chartCard').style.display = 'block';
        drawChart(data.x_values, data.y_values, data.trapezoid_points, formData);
        
        // Re-render MathJax
        if (window.MathJax) {
            MathJax.typesetPromise();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Terjadi kesalahan dalam perhitungan');
    });
});

function drawChart(xValues, yValues, trapezoidPoints, formData) {
    const ctx = document.getElementById('functionChart').getContext('2d');
    
    // Clear previous chart
    if (window.myChart) {
        window.myChart.destroy();
    }
    
    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: xValues.map(x => x.toFixed(2)),
            datasets: [{
                label: `f(x) = ${formData.function}`,
                data: yValues,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Trapesium',
                data: trapezoidPoints.map((point, i) => ({x: xValues[i], y: point})),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                fill: false,
                tension: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Visualisasi Metode Trapesium untuk f(x) = ${formData.function}`
                },
                legend: {
                    display: true
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'x'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'f(x)'
                    }
                }
            }
        }
    });
}
</script>
{% endblock %}
    """
    
    # Simpson page
    simpson_template = """
{% extends "base.html" %}
{% block title %}Metode Simpson 1/3 - Kalkulator Integral{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h3 class="mb-0">📈 Metode Simpson 1/3</h3>
            </div>
            <div class="card-body">
                <form id="simpsonForm">
                    <div class="mb-3">
                        <label class="form-label">Fungsi f(x):</label>
                        <input type="text" class="form-control" id="function" value="x**2" placeholder="Contoh: x**2, sin(x), exp(x)">
                        <small class="form-text text-muted">Gunakan sintaks Python: x**2, sin(x), cos(x), exp(x), log(x)</small>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Batas Bawah (a):</label>
                                <input type="number" class="form-control" id="lower_bound" value="0" step="0.1">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Batas Atas (b):</label>
                                <input type="number" class="form-control" id="upper_bound" value="2" step="0.1">
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Jumlah Subinterval (n):</label>
                        <input type="number" class="form-control" id="n_intervals" value="10" min="2" step="2">
                        <small class="form-text text-muted">Harus genap untuk metode Simpson 1/3</small>
                    </div>
                    
                    <button type="submit" class="btn btn-success w-100 btn-lg">
                        <i class="fas fa-calculator"></i> Hitung Integral
                    </button>
                </form>
                
                <div class="mt-4">
                    <h5>Formula Simpson 1/3:</h5>
                    <div class="alert alert-light">
                        $$I \\approx \\frac{h}{3}[f(a) + 4\\sum_{i=odd}f(x_i) + 2\\sum_{i=even}f(x_i) + f(b)]$$
                        <br><small>dimana $h = \\frac{b-a}{n}$</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card result-card" id="resultCard" style="display: none;">
            <div class="card-header bg-info text-white">
                <h4 class="mb-0">📊 Hasil Perhitungan</h4>
            </div>
            <div class="card-body">
                <div id="results"></div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card" id="chartCard" style="display: none;">
            <div class="card-header">
                <h4>📈 Visualisasi Grafik</h4>
            </div>
            <div class="card-body">
                <div id="chart-container">
                    <canvas id="functionChart" width="800" height="400"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('simpsonForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        function: document.getElementById('function').value,
        lower_bound: parseFloat(document.getElementById('lower_bound').value),
        upper_bound: parseFloat(document.getElementById('upper_bound').value),
        n_intervals: parseInt(document.getElementById('n_intervals').value)
    };
    
    // Validate even number for Simpson
    if (formData.n_intervals % 2 !== 0) {
        alert('Jumlah subinterval harus genap untuk metode Simpson 1/3');
        return;
    }
    
    fetch('/calculate_simpson', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Show results
        document.getElementById('resultCard').style.display = 'block';
        document.getElementById('results').innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="alert alert-success">
                        <h6>Hasil Simpson 1/3:</h6>
                        <strong>${data.simpson_result.toFixed(6)}</strong>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="alert alert-info">
                        <h6>Nilai Analitik:</h6>
                        <strong>${data.analytical_result ? data.analytical_result.toFixed(6) : 'Tidak tersedia'}</strong>
                    </div>
                </div>
            </div>
            ${data.analytical_result ? `
            <div class="row">
                <div class="col-md-6">
                    <div class="alert alert-warning">
                        <h6>Galat Absolut:</h6>
                        <strong>${Math.abs(data.simpson_result - data.analytical_result).toFixed(6)}</strong>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="alert alert-danger">
                        <h6>Galat Relatif:</h6>
                        <strong>${(Math.abs(data.simpson_result - data.analytical_result) / Math.abs(data.analytical_result) * 100).toFixed(4)}%</strong>
                    </div>
                </div>
            </div>
            ` : ''}
            <div class="alert alert-secondary">
                <small><strong>Parameter:</strong> h = ${((formData.upper_bound - formData.lower_bound) / formData.n_intervals).toFixed(4)}, n = ${formData.n_intervals}</small>
            </div>
        `;
        
        // Show chart
        document.getElementById('chartCard').style.display = 'block';
        drawChart(data.x_values, data.y_values, data.simpson_points, formData);
        
        // Re-render MathJax
        if (window.MathJax) {
            MathJax.typesetPromise();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Terjadi kesalahan dalam perhitungan');
    });
});

function drawChart(xValues, yValues, simpsonPoints, formData) {
    const ctx = document.getElementById('functionChart').getContext('2d');
    
    // Clear previous chart
    if (window.myChart) {
        window.myChart.destroy();
    }
    
    window.myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: xValues.map(x => x.toFixed(2)),
            datasets: [{
                label: `f(x) = ${formData.function}`,
                data: yValues,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'Simpson 1/3',
                data: simpsonPoints.map((point, i) => ({x: xValues[i], y: point})),
                borderColor: 'rgb(153, 102, 255)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                fill: false,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Visualisasi Metode Simpson 1/3 untuk f(x) = ${formData.function}`
                },
                legend: {
                    display: true
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'x'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'f(x)'
                    }
                }
            }
        }
    });
}
</script>
{% endblock %}
    """
    
    # Write templates
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(base_template)
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(home_template)
    
    with open('templates/trapesium.html', 'w', encoding='utf-8') as f:
        f.write(trapesium_template)
    
    with open('templates/simpson.html', 'w', encoding='utf-8') as f:
        f.write(simpson_template)

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
        
        return jsonify({
            'trapesium_result': trap_result,
            'analytical_result': analytical,
            'x_values': x_smooth.tolist(),
            'y_values': y_smooth,
            'trapezoid_points': y_vals
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
        
        # Calculate using Simpson's rule
        simpson_result, x_vals, y_vals =    