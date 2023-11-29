import RPi.GPIO as GPIO
import time

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

# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Set up each pin as an input and enable the internal pull-down resistor
for pin in pins.keys():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialize a dictionary to keep track of the last known pin states
last_states = {pin: GPIO.input(pin) for pin in pins.keys()}

try:
    print("Monitoring GPIO pins...")
    while True:
        for pin, name in pins.items():
            current_state = GPIO.input(pin)
            if current_state != last_states[pin]:
                # State has changed
                last_states[pin] = current_state
                state_str = "HIGH" if current_state else "LOW"
                print(f"{name} (Pin {pin}) changed to {state_str}")

        # Small delay to reduce CPU usage
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopping GPIO monitoring")

finally:
    # Clean up GPIO on exit
    GPIO.cleanup()
