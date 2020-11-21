import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


def timed_power(led_pin, duration):
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(led_pin, GPIO.LOW)


def power_on(led_id):
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.HIGH)


def power_off(led_id):
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.LOW)


for i in range(4):
    for led_pin in [12, 16, 18, 22, 32]:
        timed_power(led_pin, 0.25)


for i in range(4):
    for led_pin in [12, 16, 18, 22, 32]:
        power_on(led_pin)
    time.sleep(0.5)
    for led_pin in [12, 16, 18, 22, 32]:
        power_off(led_pin)
    time.sleep(0.5)
