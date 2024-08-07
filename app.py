from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

# Physical constants
e = 1.602e-19  # Electron charge (C)
k = 1.38e-23   # Boltzmann constant (J/K)

# Default PV cell parameters
default_Iph = 5        # Photocurrent (A)
I0 = 0.0002    # Reverse saturation current (A)
Rs = 0.001     # Series resistance (Ohms)
A = 1.2        # Curve fitting factor
default_Tc = 293.15    # Cell temperature (K)

# Function to calculate cell voltage (V)
def calc_voltage(I_C, Iph, I0, Rs, A, Tc, e, k):
    return (A * k * Tc / e) * np.log((Iph + I0 - I_C) / I0) - I_C * Rs

# Function to compute PV and IV characteristics
def compute_pv_iv(Iph, Tc, num_series, num_parallel):
    I_C_range = np.linspace(0, Iph, 100)  # Range of output currents (A)
    V_C_array = np.zeros_like(I_C_range)
    P_array = np.zeros_like(I_C_range)

    # Compute voltage and power for each current
    for i, I_C in enumerate(I_C_range):
        V_C = calc_voltage(I_C, Iph, I0, Rs, A, Tc, e, k) * num_series
        I_C_total = I_C * num_parallel
        V_C_array[i] = V_C
        P_array[i] = V_C * I_C_total

    return V_C_array, I_C_range, P_array

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    num_series = int(data['num_series'])
    num_parallel = int(data['num_parallel'])
    ambient_temp = float(data['ambient_temp'])
    solar_irradiance = float(data['solar_irradiance'])

    # Calculate photocurrent based on solar irradiance
    Iph = default_Iph * (solar_irradiance / 1000)  # Assuming 1000 W/m² is standard
    Tc = default_Tc + (ambient_temp - 25)  # Adjust cell temperature based on ambient temperature

    V_C_array, I_C_range, P_array = compute_pv_iv(Iph, Tc, num_series, num_parallel)
    return jsonify({
        'voltage': V_C_array.tolist(),
        'current': I_C_range.tolist(),
        'power': P_array.tolist()
    })

if __name__ == '__main__':
    app.run(debug=True)
