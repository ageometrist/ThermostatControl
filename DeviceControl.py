import smbus2
import bme280
import os
import time
import pytz
import datetime

debug = True
if debug:
    from gpiozero import LED

def initialize_Sensors():
    # BME280 sensor address (default address)
    address = 0x76

    if debug:
        bus = 1
        calibration_params = None
        gpio = NotImplemented
    else:
        # Initialize I2C bus
        bus = smbus2.SMBus(1)
        gpio = LED(17)
        # Load calibration parameters
        calibration_params = bme280.load_calibration_params(bus, address)
    return bus, address, calibration_params, gpio

def Read_Sensors(bus, address, calibration_params):
    # Adjust timezone
    # Define the timezone you want to use (list of timezones: https://gist.github.com/mjrulesamrat/0c1f7de951d3c508fb3a20b4b0b33a98)
    desired_timezone = pytz.timezone('America/New_York')  # Replace with your desired timezone
    
    if debug:
        temperature_celsius = 25.0
        humidity = 50.0
        pressure = 1013.25
        timestamp = datetime.datetime.utcnow()
    else:
        # Read sensor data
        data = bme280.sample(bus, address, calibration_params)

        # Extract temperature, pressure, humidity, and corresponding timestamp
        temperature_celsius = data.temperature
        humidity = data.humidity
        pressure = data.pressure
        timestamp = data.timestamp

    # Convert the datetime to the desired timezone
    timestamp = timestamp.replace(tzinfo=pytz.utc).astimezone(desired_timezone)

    # Convert temperature to Fahrenheit
    temperature_fahrenheit = (temperature_celsius * 9/5) + 32

    return temperature_celsius, humidity, pressure, timestamp, temperature_fahrenheit

def TurnPelletStoveOn(gpio, state):
    if debug:
        if state:
            print("Pellet Stove ON")
        else:
            print("Pellet Stove OFF")
    else:
        if state:
            gpio.on()
        else:
            gpio.off()
