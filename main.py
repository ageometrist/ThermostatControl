import smbus2
import bme280
import os
import time
import pytz
from gpiozero import LED
import datetime

debug = False

def initialize_Sensors():
    # BME280 sensor address (default address)
    address = 0x76

    if debug:
        bus = 1
        calibration_params = None
    else:
        # Initialize I2C bus
        bus = smbus2.SMBus(1)
        
        # Load calibration parameters
        calibration_params = bme280.load_calibration_params(bus, address)
    return bus, address, calibration_params

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

def __main__():
    bus, address, calibration_params = initialize_Sensors()

    # create a variable to control the while loop
    running = True

    # Check if the file exists before opening it in 'a' mode (append mode)
    file_exists = os.path.isfile('sensor_readings_bme280.txt')
    file = open('sensor_readings_bme280.txt', 'a')

    # Write the header to the file if the file does not exist
    if not file_exists:
        file.write('Time and Date, temperature (ºC), temperature (ºF), humidity (%), pressure (hPa)\n')
    led = LED(17)

    
    # loop forever
    while running:
        try:
            temperature_celsius, humidity, pressure, timestamp_tz, temperature_fahrenheit = Read_Sensors(bus, address, calibration_params)
            # Print the readings
            print(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + " Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%, Pressure={3:0.2f}hPa".format(temperature_celsius, temperature_fahrenheit, humidity, pressure))

            # Save time, date, temperature, humidity, and pressure in .txt file
            file.write(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + ', {:.2f}, {:.2f}, {:.2f}, {:.2f}\n'.format(temperature_celsius, temperature_fahrenheit, humidity, pressure))
            led.on()
            time.sleep(3)
            led.off()
            time.sleep(3)

        except KeyboardInterrupt:
            print('Program stopped')
            running = False
            file.close()
        except Exception as e:
            print('An unexpected error occurred:', str(e))
            running = False
            file.close()

if __name__ == "__main__":
    __main__()