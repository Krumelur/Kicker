class GPIOBase:
	def __init__(self):
		pass

	def add_event_detect(self, pin, callback, bouncetime=10):
		raise NotImplementedError

	def cleanup(self):
		raise NotImplementedError


class RaspberryPiGPIO(GPIOBase):
	def __init__(self):
		super().__init__()
		import RPi.GPIO as GPIO
		self.gpio = GPIO
		self.gpio.setmode(self.GPIO.BCM)

	def add_event_detect(self, pin, callback, bouncetime=10):
		self.gpio.setup(pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)
		self.gpio.add_event_detect(self.pin, self.GPIO.RISING, callback=callback, bouncetime=bouncetime)
		
	def cleanup(self):
		self.gpio.cleanup()


class MockGPIO(GPIOBase):
	def __init__(self):
		super().__init__()
		
	def add_event_detect(self, pin, callback, bouncetime=10):
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
	gpio_test.add_event_detect(6, test_pin_callback)
	gpio_test.cleanup()
