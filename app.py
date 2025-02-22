import serial
import time
import re
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, jsonify

# Load Firebase credentials
cred = credentials.Certificate("rpitester-firebase-adminsdk-fbsvc-2c2870fbf2.json")  # Ensure this file is in your project directory
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://rpitester-default-rtdb.firebaseio.com/"  # Replace with your Firebase URL
})

# Initialize Serial Connection (Modify based on your Arduino's port)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Allow Arduino time to initialize

app = Flask(__name__)

def read_serial_data():
    """ Reads and sends Arduino sensor data to Firebase """
    try:
        ser.flush()
        data = []

        for _ in range(5):  # Read multiple lines
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Received: {line}")

            match = re.search(r"[-+]?\d*\.\d+|\d+", line)  # Extract numbers
            if match:
                data.append(float(match.group()))

        if len(data) >= 4:
            temperature, humidity, pressure, water_level = data[:4]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            sensor_data = {
                "timestamp": timestamp,
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "pressure": round(pressure, 2),
                "water_level": "Detected" if int(water_level) == 1 else "Not Detected",
            }

            # Store data in Firebase (Realtime Database)
            db.reference("sensor_data").push(sensor_data)

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
    """ API route to get the latest sensor data """
    ref = db.reference("sensor_data").order_by_key().limit_to_last(1).get()
    latest_entry = list(ref.values())[0] if ref else None

    if latest_entry:
        return jsonify(latest_entry)
    return jsonify({"error": "No data available"}), 500

@app.route("/history")
def get_history():
    """ API route to get historical sensor data """
    ref = db.reference("sensor_data").order_by_key().limit_to_last(100).get()
    history_data = list(ref.values()) if ref else []
    
    return jsonify(history_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
