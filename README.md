# Autonomous Raspberry Pi Robot Truck — Plant Care

**Short name:** Robot Plant Care  
**Platform:** Raspberry Pi 4 Model B (64-bit Raspberry Pi OS)  
**Status:** Prototype / Lab-tested components. See `test_sensors.py` for individual sensor diagnostics.

---

## Project Overview

This project develops an autonomous robot truck designed to assist with plant care. The robot follows a human instructor (forward/backward motion only), carries heavy items passively, detects fire and humidity anomalies, waters plants using a mini pump, evaluates plant health via USB camera color analysis, and provides alerts through a buzzer and RGB LED. Status updates are displayed on a 16×2 LCD.

All behavior, GPIO pin assignments, thresholds, and file structures adhere to the exact specifications used during development.

---

## Features

- **Human Following**: Uses an **HC-SR04** ultrasonic sensor for distance-based movement (forward, backward, stop).
- **Fire Detection**: Primary detection via flame sensor (active low); backup detection via rapid temperature rise from **DHT22**.
- **Humidity Monitoring**: Alerts for low humidity levels using **DHT22**.
- **Plant Watering**: Activates a mini water pump via relay for 3 seconds upon fire detection.
- **Plant Health Assessment**: Analyzes plant health using USB camera with HSV-based green color detection.
- **Alerts**: Notifies via **active buzzer** (short or continuous beeps) and **RGB LED** (color-coded flashing).
- **Status Display**: Shows real-time status and warnings on a **16×2 LCD** (messages truncated to 16 characters per line).
- **Performance**: Main loop runs every ~0.1 seconds with safe GPIO cleanup on program exit.

---

## Hardware Requirements

- **Raspberry Pi 4 Model B** running 64-bit Raspberry Pi OS
- **L298N Motor Driver** controlling four DC motors (wired as two pairs)
- **HC-SR04 Ultrasonic Sensor** for distance measurement
- **Flame Sensor (ref 0900690)** with digital output (active low)
- **DHT22 Sensor** for temperature and humidity monitoring
- **Active Buzzer (ref 0900590)** for audible alerts
- **USB Camera** for plant health color analysis
- **RGB LED (common anode)** with ports for GND, R, G, B (HIGH to light)
- **Mini Water Pump** controlled via a single-channel relay module
- **16×2 LCD** (configured for 4-bit GPIO wiring; I²C optional)
- **Breadboard, Resistors, Wires**:
  - Voltage divider for HC-SR04 Echo pin (e.g., 1 kΩ series, 2.2 kΩ to ground) to step down 5V to ~3.3V
- **Power**:
  - External 5–12V battery for motors and pump
  - Raspberry Pi powered via USB
  - Ensure **common ground** between Pi and external battery

---

## GPIO Pin Mapping (BCM Mode)

> **Critical**: Do not modify pin assignments to maintain compatibility with the codebase.

- **Motors (L298N)**:
  - IN1: `GPIO 5`
  - IN2: `GPIO 6`
  - IN3: `GPIO 13`
  - IN4: `GPIO 19`
- **Flame Sensor (Digital D)**: `GPIO 18` (input, active low)
- **Pump Relay**: `GPIO 17` (output, HIGH activates)
- **Active Buzzer**: `GPIO 22` (output, active high)
- **HC-SR04 Ultrasonic Sensor**:
  - TRIG: `GPIO 23` (output)
  - ECHO: `GPIO 24` (input via voltage divider)
- **DHT22 Data**: `GPIO 4`
- **RGB LED** (common anode):
  - R: `GPIO 11`
  - G: `GPIO 9`
  - B: `GPIO 10` (HIGH to light)
- **16×2 LCD (4-bit wiring)**:
  - RS: `GPIO 8`
  - E: `GPIO 7`
  - D4: `GPIO 12`
  - D5: `GPIO 16`
  - D6: `GPIO 20`
  - D7: `GPIO 25`

> **Echo Pin Safety**: Always use a voltage divider on the HC-SR04 Echo pin to protect the Raspberry Pi from 5V signals.

---

## Thresholds and Behavior

- **Humidity Alert**: Triggers if humidity falls below `40.0%`.
- **Distance Control** (via HC-SR04, in cm):
  - `> 150`: STOP (too far)
  - `50–100`: FORWARD (buzzer beeps if `< 60`)
  - `30–50`: BACKWARD (buzzer beeps)
  - `< 30`: STOP, continuous buzzer, triggers plant health check
- **Fire Detection**:
  - Primary: Flame sensor (active low) triggers immediate action.
  - Backup: DHT22 detects temperature rise `> 10.0°C` per loop (~0.1s).
- **Plant Health**:
  - USB camera checks green percentage using HSV color mask:
    - Lower bound: `[35, 50, 50]`
    - Upper bound: `[85, 255, 255]`
    - Healthy threshold: `> 50.0%` green pixels
- **Pump Activation**: Runs for `3 seconds` on fire detection.
- **Buzzer Alerts**:
  - Short beeps: `0.5–1 second` for warnings.
  - Continuous: During danger state (`< 30 cm`).
- **RGB LED Alerts**:
  - Flashes `3 times` at `0.5s` on/off for fire or plant health issues.

---

## Repository Structure

```
~/myproject/
├── requirements.txt       # Python dependencies
├── run_robot.sh          # Shell script to run the main program
└── src/
    ├── app.py            # Main control loop
    ├── gpio_config.py    # GPIO pin and threshold definitions
    ├── robot_controller.py # Motor and sensor control logic
    ├── lcd_display.py    # 16×2 LCD interface (4-bit wiring)
    ├── dht22_sensor.py   # DHT22 sensor wrapper
    ├── camera_utils.py   # USB camera capture and HSV analysis
    ├── test_sensors.py   # Sensor diagnostic tests
    └── diseases.json     # Plant health alert messages
```

---

## Software Installation

1. **Update System and Install Dependencies** (run outside virtual environment):
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y i2c-tools
sudo apt install -y libgpiod2 || sudo apt install -y libgpiod3 || true

# Fix libgpiod if necessary (e.g., if libgpiod.so.3 exists but .so.2 is required):
sudo ln -s /usr/lib/aarch64-linux-gnu/libgpiod.so.3 /usr/lib/aarch64-linux-gnu/libgpiod.so.2 2>/dev/null || true
```

2. **Set Up Python Virtual Environment**:
```bash
cd ~/myproject
python3 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

> **Note**: If `tflite-runtime==2.14.0` fails to install, remove it from `requirements.txt` and rerun `pip install -r requirements.txt`. This package is optional and not critical for core functionality.

---

## Running and Testing

1. **Activate Virtual Environment**:
```bash
cd ~/myproject
source env/bin/activate
```

2. **Run Sensor Tests**:
```bash
python3 src/test_sensors.py
```
> Displays sensor readings on terminal and LCD for verification.

3. **Run Main Program**:
```bash
python3 src/app.py
```

4. **Run Demo Script** (for quick fire/humidity alerts):
```bash
python3 src/alert_lcd.py  # Optional, if included
```

---

## Troubleshooting

- **libgpiod.so.2/PulseIn Errors**: Ensure `libgpiod2` or `libgpiod3` is installed. Create a symlink if needed (see installation).
- **tflite-runtime Failure**: Remove `tflite-runtime` from `requirements.txt` (not required).
- **Adafruit_DHT "Unknown platform"**: Verify `Adafruit_DHT` is installed in the virtual environment and `libgpiod` is present. Use `read_retry` (already implemented).
- **RPLCD I²C Errors**: Install `smbus2` (`pip install smbus2`) or switch to 4-bit wiring. Run `i2cdetect -y 1` to verify I²C address.
- **HC-SR04 Erratic Readings**: Confirm voltage divider on Echo pin and check timeout handling in code (returns `None` for invalid readings).
- **LCD Not Displaying**: Verify wiring (4-bit vs. I²C) and pin assignments. Check I²C with `i2cdetect -y 1`.
- **GPIO Warnings**: Code includes `GPIO.setwarnings(False)`; ensure no other processes are accessing GPIO pins.

---

## Recording Tips for Demos

1. **Setup**: Position the camera to capture the **LCD**, **RGB LED**, and audible **buzzer** output.
2. **Test Sequence**: Use `python3 src/test_sensors.py` for a repeatable, short demonstration.
3. **Simulate Fire**: Briefly wave a small candle at a safe distance from the flame sensor or temporarily short the sensor input to trigger active-low behavior.
4. **Simulate Low Humidity**: Temporarily modify `dht22_sensor.py` or `app.py` to force a low humidity reading (revert after recording).

---

## Contributing

Contributions are welcome but must adhere to the **exact GPIO pin mappings and thresholds** specified in this README. Update the documentation for any changes to pins, thresholds, or behavior.

---

## License

Provided as-is for prototyping and educational purposes. If sharing publicly (e.g., on GitHub), consider using the MIT License.
