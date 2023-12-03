from typing import Callable, Dict
from time import sleep

class GPIOBase:
	def __init__(self):
		pass

	def set_callback(self, pin, callback, bouncetime=10):
		raise NotImplementedError

	def cleanup(self):
		raise NotImplementedError


class RaspberryPiGPIO(GPIOBase):
	def __init__(self):
		super().__init__()
		import RPi.GPIO as GPIO
		self.GPIO = GPIO
		self.GPIO.setmode(self.GPIO.BCM)
		self.callback_map : Dict[int, Callable] = {}

	def inner_callback(self, channel:int):
		sleep(0.005) # edge debounce of 5ms
		if self.GPIO.input(channel) == 0:
			return
		
		if channel in self.callback_map:
			self.callback_map[channel](channel)
		else:
			raise ValueError(f"No callback registered for channel {channel}")
		
	def set_callback(self, pin:int, callback:Callable, bouncetime_ms:int):
		self.callback_map[pin] = callback
		self.GPIO.setup(pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)
		self.GPIO.add_event_detect(pin, self.GPIO.RISING, callback=self.inner_callback, bouncetime=bouncetime_ms)
		
	def cleanup(self):
		self.GPIO.cleanup()
		self.callback_map.clear()


class MockGPIO(GPIOBase):
	def __init__(self):
		super().__init__()
		
	def set_callback(self, pin, callback, bouncetime=10):
		print("Mock: Adding event detection on pin", pin)

	def cleanup(self):
		print("Cleaning up GPIO")

if __name__ == "__main__":
	import sys
	
	def test_pin_callback(channel):
		print("Pin", channel, "changed to high")

	if sys.platform == "darwin":
		gpio_test = MockGPIO()
	else:
		gpio_test = RaspberryPiGPIO()
	gpio_test.set_callback(6, test_pin_callback)
	input("Press Enter to continue...")
	gpio_test.cleanup()
