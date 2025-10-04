# gpio_config.py
class GPIOConfig:
    # Motors (L298N)
    IN1 = 5
    IN2 = 6
    IN3 = 13
    IN4 = 19

    # Flame sensor (digital, active low)
    FLAME_PIN = 18

    # Pump relay (active high)
    PUMP_PIN = 17

    # Buzzer (active high)
    BUZZER_PIN = 22

    # HC-SR04 Ultrasonic
    TRIG_PIN = 23
    ECHO_PIN = 24

    # DHT22
    DHT_PIN = 4

    # RGB LED (per spec: R=11,G=9,B=10)
    LED_R = 11
    LED_G = 9
    LED_B = 10

    # LCD pins (BCM for 4-bit mode)
    LCD_RS = 8
    LCD_E = 7
    LCD_D4 = 12
    LCD_D5 = 16
    LCD_D6 = 20
    LCD_D7 = 25

    # I2C address if using i2c expander (not used here)
    LCD_I2C_ADDR = 0x27


class Thresholds:
    HUMIDITY_LOW = 40.0

    # Distances (cm)
    DIST_TOO_FAR = 150.0
    DIST_IDEAL_LOW = 50.0
    DIST_IDEAL_HIGH = 100.0
    DIST_CLOSE_LOW = 30.0
    DIST_CLOSE_HIGH = 50.0
    DIST_DANGER = 30.0

    TEMP_RISE_FIRE = 10.0  # degrees C per loop

    # Green detection
    GREEN_LOWER = (35, 50, 50)
    GREEN_UPPER = (85, 255, 255)
    GREEN_PERCENT_HEALTHY = 50.0

    PUMP_DURATION = 3.0
    BUZZER_SHORT = 0.5
    BUZZER_LONG = 1.0
    BUZZER_CONTINUOUS = 3.0
    LED_FLASH_COUNT = 3
    LED_FLASH_DURATION = 0.5

    # Ultrasonic validity
    ULTRASONIC_MIN = 2.0
    ULTRASONIC_MAX = 400.0
