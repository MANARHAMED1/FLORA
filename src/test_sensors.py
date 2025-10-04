# test_sensors.py
import time
from lcd_display import display_message, clear
from robot_controller import RobotController
from dht22_sensor import DHT22Sensor
from camera_utils import capture_frame, is_healthy_by_color

def main():
    rc = RobotController()
    dht = DHT22Sensor()
    try:
        print("LCD test")
        display_message("Test LCD\nLine2 OK")
        time.sleep(2)
        clear()

        print("RGB LED test")
        rc.set_rgb(True, False, False); time.sleep(1)
        rc.set_rgb(False, True, False); time.sleep(1)
        rc.set_rgb(False, False, True); time.sleep(1)
        rc.set_rgb(False, False, False)

        print("Ultrasonic test")
        d = rc.get_distance()
        print("Distance:", d)
        time.sleep(1)

        print("Camera test")
        frame = capture_frame()
        healthy, pct = is_healthy_by_color(frame)
        print("Healthy:", healthy, "Green%:", pct)
        time.sleep(1)

        print("Flame:", rc.flame_detected())
        print("Buzzer test")
        rc.sound_buzzer(1.0)
        time.sleep(0.5)

        print("Pump test (3s)")
        rc.activate_pump(3.0)

    finally:
        rc.cleanup()
        clear()
        print("Tests finished.")

if __name__ == "__main__":
    main()
