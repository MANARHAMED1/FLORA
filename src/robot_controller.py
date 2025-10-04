# robot_controller.py
import RPi.GPIO as GPIO
import time
import statistics
from gpio_config import GPIOConfig, Thresholds

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class RobotController:
    def __init__(self):
        # motors pins
        for p in (GPIOConfig.IN1, GPIOConfig.IN2, GPIOConfig.IN3, GPIOConfig.IN4):
            if p is not None:
                GPIO.setup(p, GPIO.OUT)
                GPIO.output(p, False)

        # buzzer and RGB
        for p in (GPIOConfig.BUZZER_PIN, GPIOConfig.LED_R, GPIOConfig.LED_G, GPIOConfig.LED_B):
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, False)

        # flame
        GPIO.setup(GPIOConfig.FLAME_PIN, GPIO.IN)

        # ultrasonic
        GPIO.setup(GPIOConfig.TRIG_PIN, GPIO.OUT)
        GPIO.setup(GPIOConfig.ECHO_PIN, GPIO.IN)
        GPIO.output(GPIOConfig.TRIG_PIN, False)
        time.sleep(0.05)

    # RGB control (HIGH lights per spec)
    def set_rgb(self, r=False, g=False, b=False):
        GPIO.output(GPIOConfig.LED_R, bool(r))
        GPIO.output(GPIOConfig.LED_G, bool(g))
        GPIO.output(GPIOConfig.LED_B, bool(b))

    def flash_rgb(self, color, count=Thresholds.LED_FLASH_COUNT, duration=Thresholds.LED_FLASH_DURATION):
        for _ in range(count):
            if color == 'red':
                self.set_rgb(True, False, False)
            elif color == 'green':
                self.set_rgb(False, True, False)
            elif color == 'blue':
                self.set_rgb(False, False, True)
            elif color == 'yellow':
                self.set_rgb(True, True, False)
            else:
                self.set_rgb(False, False, False)
            time.sleep(duration)
            self.set_rgb(False, False, False)
            time.sleep(duration)

    # buzzer helpers
    def sound_buzzer(self, duration=Thresholds.BUZZER_SHORT):
        GPIO.output(GPIOConfig.BUZZER_PIN, True)
        time.sleep(duration)
        GPIO.output(GPIOConfig.BUZZER_PIN, False)

    def sound_buzzer_continuous(self):
        GPIO.output(GPIOConfig.BUZZER_PIN, True)

    def stop_buzzer(self):
        GPIO.output(GPIOConfig.BUZZER_PIN, False)

    # pump
    def activate_pump(self, duration=Thresholds.PUMP_DURATION):
        try:
            GPIO.setup(GPIOConfig.PUMP_PIN, GPIO.OUT)
            GPIO.output(GPIOConfig.PUMP_PIN, True)
            time.sleep(duration)
            GPIO.output(GPIOConfig.PUMP_PIN, False)
        except Exception:
            pass

    # motors basic control
    def move_forward(self):
        GPIO.output(GPIOConfig.IN1, True)
        GPIO.output(GPIOConfig.IN2, False)
        GPIO.output(GPIOConfig.IN3, True)
        GPIO.output(GPIOConfig.IN4, False)

    def move_backward(self):
        GPIO.output(GPIOConfig.IN1, False)
        GPIO.output(GPIOConfig.IN2, True)
        GPIO.output(GPIOConfig.IN3, False)
        GPIO.output(GPIOConfig.IN4, True)

    def stop(self):
        GPIO.output(GPIOConfig.IN1, False)
        GPIO.output(GPIOConfig.IN2, False)
        GPIO.output(GPIOConfig.IN3, False)
        GPIO.output(GPIOConfig.IN4, False)

    # flame detect (active low)
    def flame_detected(self, samples=3, interval=0.05):
        for _ in range(samples):
            val = GPIO.input(GPIOConfig.FLAME_PIN)
            if val != 0:
                return False
            time.sleep(interval)
        return True

    # ultrasonic robust
    def _single_distance(self, timeout=0.04):
        GPIO.output(GPIOConfig.TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(GPIOConfig.TRIG_PIN, False)

        start_time = time.time()
        stop_time = start_time

        start_echo = time.time()
        while GPIO.input(GPIOConfig.ECHO_PIN) == 0:
            start_time = time.time()
            if time.time() - start_echo > timeout:
                return None

        stop_echo = time.time()
        while GPIO.input(GPIOConfig.ECHO_PIN) == 1:
            stop_time = time.time()
            if time.time() - stop_echo > timeout:
                return None

        duration = stop_time - start_time
        distance = (duration * 34300.0) / 2.0
        if distance <= 0 or distance > Thresholds.ULTRASONIC_MAX:
            return None
        return distance

    def get_distance(self, samples=5):
        readings = []
        for _ in range(samples):
            d = self._single_distance()
            if d is not None:
                readings.append(d)
            time.sleep(0.02)
        if not readings:
            return None
        return statistics.median(readings)

    def run_auto_follow(self, distance):
        if distance is None:
            self.stop()
            self.stop_buzzer()
            return

        if distance > Thresholds.DIST_TOO_FAR:
            self.stop()
            self.stop_buzzer()
            return

        if distance < Thresholds.DIST_DANGER:
            self.stop()
            self.sound_buzzer_continuous()
            return

        if Thresholds.DIST_CLOSE_LOW <= distance < Thresholds.DIST_CLOSE_HIGH:
            self.move_backward()
            self.sound_buzzer(Thresholds.BUZZER_SHORT)
            return

        if Thresholds.DIST_IDEAL_LOW <= distance <= Thresholds.DIST_IDEAL_HIGH:
            self.move_forward()
            if distance < 60.0:
                self.sound_buzzer(Thresholds.BUZZER_SHORT)
            else:
                self.stop_buzzer()
            return

        self.stop()
        self.stop_buzzer()

    def cleanup(self):
        self.stop()
        self.stop_buzzer()
        self.set_rgb(False, False, False)
        GPIO.cleanup()
