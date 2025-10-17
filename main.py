import os
import time
import pytz
import datetime
from DeviceControl import Read_Sensors, TurnPelletStoveOn, initialize_Sensors

def __main__():
    bus, address, calibration_params, gpio = initialize_Sensors()

    # create a variable to control the while loop
    running = True

    # Check if the file exists before opening it in 'a' mode (append mode)
    file_exists = os.path.isfile('sensor_readings_bme280.txt')
    file = open('sensor_readings_bme280.txt', 'a')

    # Write the header to the file if the file does not exist
    if not file_exists:
        file.write('Time and Date, temperature (ºC), temperature (ºF), humidity (%), pressure (hPa)\n')
    

    
    # loop forever
    while running:
        try:
            temperature_celsius, humidity, pressure, timestamp_tz, temperature_fahrenheit = Read_Sensors(bus, address, calibration_params)
            # Print the readings
            print(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + " Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%, Pressure={3:0.2f}hPa".format(temperature_celsius, temperature_fahrenheit, humidity, pressure))

            # Save time, date, temperature, humidity, and pressure in .txt file
            file.write(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + ', {:.2f}, {:.2f}, {:.2f}, {:.2f}\n'.format(temperature_celsius, temperature_fahrenheit, humidity, pressure))
            TurnPelletStoveOn(gpio, True)
            time.sleep(3)
            TurnPelletStoveOn(gpio, False)
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