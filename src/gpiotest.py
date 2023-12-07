import time
from time import sleep
from gpiozero import Button
from signal import pause

pins = {
 26: 'Taster 1',
 5: 'Taster 2',
 17: 'Taster 3',
 19: 'Taster 4',
 13: 'Taster 5',
 27: 'Torsensor Schwarz',
 6: 'Torsensor Blau'
}

def button_pressed(button):
    print(f"Button on pin {button.pin.number} was pressed")
    
def button_released(button):
    print(f"Button on pin {button.pin.number} was released")

buttons = []

for pin in pins.keys():
    print(f"Setting up button {pin} '{pins[pin]}'")
    button = Button(pin)
    button.when_pressed = lambda captured_button = button: button_pressed(captured_button)
    button.when_released = lambda captured_button = button: button_released(captured_button)
    buttons.append(button)
    
pause()
