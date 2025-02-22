import serial
import time
import re
from flask import Flask, render_template, jsonify

# Initialize Serial Connection
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Allow Arduino time to initialize

app = Flask(__name__)

# Store data (acts as a buffer for recent values)
sensor_data = []

def read_serial_data():
    """ Reads and parses data from the Arduino serial output """
    try:
        ser.flush()
        data = []

        # Read multiple lines to ensure we get all sensor data
        for _ in range(5):  # Arduino prints 5 lines per cycle
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Received: {line}")  # Debugging output

            # Extract numerical values from the received line
            match = re.search(r"[-+]?\d*\.\d+|\d+", line)  # Extract first number in line
            if match:
                data.append(float(match.group()))

        # Ensure we have all expected values before returning
        if len(data) >= 4:
            temperature, humidity, pressure, water_level = data[:4]
            entry = {
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "pressure": round(pressure, 2),
                "water_level": "Detected" if int(water_level) == 1 else "Not Detected",
                "timestamp": time.strftime("%H:%M:%S")
            }

            # Store latest 100 entries (preventing unlimited growth)
            sensor_data.append(entry)
            if len(sensor_data) > 100:
                sensor_data.pop(0)

            return entry
    except Exception as e:
        print(f"Serial Read Error: {e}")

    return None

@app.route("/")
def index():
    """ Render the HTML page """
    return render_template("index.html")

@app.route("/data")
def get_data():
    """ API route to send the latest sensor data """
    data = read_serial_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Failed to read from Arduino"}), 500

@app.route("/history")
def get_history():
    """ API route to return historical sensor data """
    return jsonify(sensor_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
