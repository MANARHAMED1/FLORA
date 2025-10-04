# lcd_display.py
from RPLCD.gpio import CharLCD
from gpio_config import GPIOConfig
import time

# Using 4-bit direct wiring per spec (RS=8,E=7,D4=12,D5=16,D6=20,D7=25)
lcd = CharLCD(cols=16, rows=2, pin_rs=GPIOConfig.LCD_RS, pin_e=GPIOConfig.LCD_E,
              pins_data=[GPIOConfig.LCD_D4, GPIOConfig.LCD_D5, GPIOConfig.LCD_D6, GPIOConfig.LCD_D7],
              numbering_mode='BCM')

def _truncate(s):
    return str(s)[:16] if s is not None else ''

def display_message(line1):
    # support newline in single argument
    if '\n' in line1:
        parts = line1.split('\n', 1)
        l1 = _truncate(parts[0])
        l2 = _truncate(parts[1])
    else:
        l1 = _truncate(line1)
        l2 = ''
    try:
        lcd.clear()
        lcd.write_string(l1)
        lcd.cursor_pos = (1, 0)
        lcd.write_string(l2)
    except Exception:
        # fallback to console
        print("[LCD]", l1)
        if l2:
            print("[LCD]", l2)

def display_plant_result(healthy):
    if healthy:
        display_message(" Plante saine")
    else:
        display_message(" Plante malade - Verifiez!")

def clear():
    try:
        lcd.clear()
    except Exception:
        pass

def cleanup():
    try:
        lcd.clear()
        lcd.close()
    except Exception:
        pass
