from gpio import RaspberryPiGPIO
import RPi.GPIO as GPIO
import time
from time import sleep

# Define the GPIO pins and their names
pins = {
 26: 'Taster 1',
 5: 'Taster 2',
 17: 'Taster 3',
 19: 'Taster 4',
 13: 'Taster 5',
 27: 'Torsensor Schwarz',
 6: 'Torsensor Blau'
}


gpio = RaspberryPiGPIO()

def on_event(channel):
	name = pins[channel]
	current_state = GPIO.input(channel)
	if current_state == 1:
		state_str = "HIGH" if current_state else "LOW"
		print(f"{name} (Pin {pin}) changed to {state_str}")

# Set up each pin as an input and enable the internal pull-down resistor
for pin in pins.keys():
	gpio.set_callback(pin, on_event, 5)

try:
	print("Monitoring GPIO pins...")
	while True:
		# Small delay to reduce CPU usage
		time.sleep(0.1)
except KeyboardInterrupt:
	print("Stopping GPIO monitoring")

finally:
	# Clean up GPIO on exit
	GPIO.cleanup()
