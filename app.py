import serial
import time
import re
from flask import Flask, render_template, jsonify

# Initialize Serial Connection
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Allow Arduino time to initialize

app = Flask(__name__)

# Global variables to store data and last read time
sensor_data = None
last_read_time = 0  # Store last read timestamp

def read_serial_data():
    """ Reads and parses data from the Arduino serial output once per hour """
    global sensor_data, last_read_time

    current_time = time.time()
    if sensor_data and (current_time - last_read_time < 900):  # Check if an hour has passed
        print("Returning cached data (not reading from serial)")
        return sensor_data

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
            sensor_data = {
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "pressure": round(pressure, 2),
                "water_level": "Detected" if int(water_level) == 1 else "Not Detected",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            last_read_time = current_time  # Update last read time
            return sensor_data
    except Exception as e:
        print(f"Serial Read Error: {e}")

    return None

@app.route("/")
def index():
    """ Render the HTML page """
    return render_template("index.html")

@app.route("/data")
def get_data():
    """ API route to send sensor data (read only once per hour) """
    data = read_serial_data()
    if data:
        return jsonify(data)
    return jsonify({"error": "Failed to read from Arduino"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
