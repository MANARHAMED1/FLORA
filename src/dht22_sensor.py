# dht22_sensor.py
import Adafruit_DHT
from gpio_config import GPIOConfig

class DHT22Sensor:
    def __init__(self):
        self.sensor = Adafruit_DHT.DHT22
        self.pin = GPIOConfig.DHT_PIN

    def read(self):
        try:
            humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)
            return humidity, temperature
        except Exception:
            return None, None
