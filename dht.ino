// Include necessary libraries
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <DHT.h>

// Define DHT22 pin and type
#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Initialize BMP280
Adafruit_BMP280 bmp;

// Define sensor pins
#define WATER_LEVEL_PIN 3
#define SOIL_MOISTURE_PIN A0

// Threshold for rain detection based on soil wetness
#define RAIN_THRESHOLD_PERCENT 70 // Adjust based on your sensor and conditions

void setup() {
  Serial.begin(9600);
  dht.begin();

  if (!bmp.begin(0x76)) {
    Serial.println("Could not find a valid BMP280 sensor, check wiring!");
    while (1);
  }

  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X2,
                  Adafruit_BMP280::SAMPLING_X16,
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);

  pinMode(WATER_LEVEL_PIN, INPUT);
}

// Function to check if it's raining based on soil moisture
bool isRaining(int moistureValue, int thresholdPercent) {
  int moisturePercent = map(moistureValue, 1023, 300, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);

  Serial.print("Soil Moisture Value: ");
  Serial.println(moistureValue);
  Serial.print("Soil Moisture (%): ");
  Serial.println(moisturePercent);
  Serial.print("Rain Status: ");
  Serial.println(moisturePercent >= thresholdPercent ? "Raining" : "Not Raining");

  return (moisturePercent >= thresholdPercent);
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT22 sensor!");
  } else {
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");

    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");
  }

  float pressure = bmp.readPressure() / 100.0F;
  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" hPa");

  int waterLevel = digitalRead(WATER_LEVEL_PIN);
  Serial.print("Water Level: ");
  Serial.println(waterLevel == HIGH ? "Detected" : "Not Detected");

  // Soil moisture reading and rain detection
  int soilMoistureValue = analogRead(SOIL_MOISTURE_PIN);
  bool raining = isRaining(soilMoistureValue, RAIN_THRESHOLD_PERCENT);

  Serial.print("Is it Raining (bool): ");
  Serial.println(raining ? "true" : "false");

  Serial.println("---------------");

  delay(2000);
}
