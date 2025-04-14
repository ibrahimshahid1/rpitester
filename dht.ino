// Include necessary libraries
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <DHT.h>

// Define DHT22 pin and type
#define DHTPIN 2 // Pin connected to DHT22 data pin
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Initialize BMP280
Adafruit_BMP280 bmp;

// Define water level sensor pin
#define WATER_LEVEL_PIN 3 // Pin connected to water level sensor

void setup() {
  // Initialize Serial Monitor
  Serial.begin(9600);

  // Initialize DHT22 sensor
  dht.begin();

  // Initialize BMP280 sensor
  if (!bmp.begin(0x76)) { // 0x76 is the I2C address of BMP280
    Serial.println("Could not find a valid BMP280 sensor, check wiring!");
    while (1);
  }

  // Set BMP280 to normal mode
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,      // Normal mode
                  Adafruit_BMP280::SAMPLING_X2,     // Temperature oversampling x2
                  Adafruit_BMP280::SAMPLING_X16,    // Pressure oversampling x16
                  Adafruit_BMP280::FILTER_X16,      // Filter x16
                  Adafruit_BMP280::STANDBY_MS_500); // Standby time 500ms

  // Initialize water level sensor pin
  pinMode(WATER_LEVEL_PIN, INPUT);
}

void loop() {
  // Read temperature and humidity from DHT22
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Check if DHT22 readings are valid
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

  // Read air pressure from BMP280
  float pressure = bmp.readPressure() / 100.0F; // Convert Pa to hPa
  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" hPa");

  // Read water level sensor state
  int waterLevel = digitalRead(WATER_LEVEL_PIN);                                                                                  
  if (waterLevel == HIGH) {
    Serial.println("Water Level: Detected");
    Serial.println(waterLevel);
  } else {
    Serial.println("Water Level: Not Detected");
    Serial.println(waterLevel);
  }

  // Delay before next reading
  delay(2000);
}
