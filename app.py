import serial
import time
import re
from flask import Flask, render_template, jsonify

# Initialize Serial Connection
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Allow Arduino time to initialize

app = Flask(__name__)

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
            return {
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "pressure": round(pressure, 2),
                "water_level": "Detected" if int(water_level) == 1 else "Not Detected"
            }
    except Exception as e:
        print(f"Serial Read Error: {e}")

    return None

@app.route("/")
def index():
    """ Render the HTML page """
    return render_template("index.html")

@app.route("/data")
def get_data():
    """ API route to send sensor data as JSON """
    data = read_serial_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Failed to read from Arduino"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
