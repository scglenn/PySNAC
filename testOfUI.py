
import Adafruit_CharLCD as LCD
import time
from LCD_Control import LCD_Control

control = LCD_Control(LCD)

myInput = control.getUserInput()
print(myInput)
