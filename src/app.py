# app.py
import time
import json
from gpio_config import Thresholds
from lcd_display import display_message, display_plant_result, cleanup as lcd_cleanup
from robot_controller import RobotController
from dht22_sensor import DHT22Sensor
from camera_utils import capture_frame, is_healthy_by_color

with open("src/diseases.json", "r", encoding="utf-8") as f:
    DISEASES = json.load(f)

def main():
    controller = RobotController()
    dht = DHT22Sensor()
    prev_temp = None

    try:
        display_message("Robot Plant Care\nStarting...")
        time.sleep(1)

        while True:
            # DHT read (backup fire detection + humidity low)
            humidity, temperature = dht.read()
            if humidity is not None and temperature is not None:
                display_message(f"Hum:{humidity:.1f}%\nTmp:{temperature:.1f}C")
                if humidity < Thresholds.HUMIDITY_LOW:
                    controller.set_rgb(False, False, True)  # blue
                    display_message(f"Low humidity\n{humidity:.1f}%")
                if prev_temp is not None and (temperature - prev_temp) > Thresholds.TEMP_RISE_FIRE:
                    display_message("DETECTION FEU\nTemp rise")
                    controller.set_rgb(True, False, False)
                    controller.sound_buzzer(Thresholds.BUZZER_CONTINUOUS)
                    controller.activate_pump(Thresholds.PUMP_DURATION)
                    controller.stop_buzzer()
                    display_message("Extinction done\n")
                prev_temp = temperature
            else:
                display_message("DHT read failed\n")

            # Flame sensor (primary)
            if controller.flame_detected():
                controller.stop()
                display_message("DETECTION FLAMME\nExtinction ...")
                controller.set_rgb(True, False, False)
                controller.sound_buzzer_continuous()
                controller.activate_pump(Thresholds.PUMP_DURATION)
                controller.sound_buzzer(Thresholds.BUZZER_CONTINUOUS)
                controller.stop_buzzer()
                controller.set_rgb(False, False, False)
                time.sleep(0.5)

            # Distance & follow
            distance = controller.get_distance()
            if distance is None:
                display_message("Distance: N/A\n")
                controller.stop()
            else:
                display_message(f"Dist:{distance:.1f}cm\n")
                if distance < Thresholds.DIST_DANGER:
                    controller.stop()
                    frame = capture_frame()
                    healthy, green_percent = is_healthy_by_color(frame)
                    if healthy is None:
                        display_message("Cam fail\n")
                    elif healthy:
                        controller.set_rgb(False, True, False)
                        display_message(DISEASES.get("healthy", " Plante saine") + f"\n{green_percent:.1f}%")
                    else:
                        for _ in range(Thresholds.LED_FLASH_COUNT):
                            controller.set_rgb(True, True, False)
                            time.sleep(Thresholds.LED_FLASH_DURATION)
                            controller.set_rgb(False, False, False)
                            time.sleep(Thresholds.LED_FLASH_DURATION)
                        controller.sound_buzzer(Thresholds.BUZZER_LONG)
                        display_message(DISEASES.get("sick", " Plante malade - Vérifiez!") + f"\n{green_percent:.1f}%")
                    time.sleep(1.0)
                else:
                    controller.run_auto_follow(distance)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("User interrupt - exiting")
    finally:
        controller.cleanup()
        lcd_cleanup()

if __name__ == "__main__":
    main()
