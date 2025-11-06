import os
import time
import pytz
import datetime
import numpy as np
import sys
from DeviceControl import Read_Sensors, TurnPelletStoveOn, initialize_Sensors, GetTrueTemperature
import Schedule

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
    
    lastTemps = np.ndarray(10)
    trueTemperature = 0
    pellletStoveState = False

    currentSchedule = Schedule.Schedule()

    timeTurnedOn: datetime.datetime = None
    timeTurnedOff: datetime.datetime = None

    # set up a simple schedule with the same schedule every day
    for day in range(7):
        currentSchedule.add_schedule(day, datetime.time(0, 0), datetime.time(4, 0), 61.0) 
        currentSchedule.add_schedule(day, datetime.time(4, 0), datetime.time(11, 0), 70.0)
        currentSchedule.add_schedule(day, datetime.time(11, 0), datetime.time(16, 0), 68.0) 
        currentSchedule.add_schedule(day, datetime.time(16, 0), datetime.time(18, 0), 70.0)
        currentSchedule.add_schedule(day, datetime.time(18, 0), datetime.time(23, 59), 61.0)
    
    # loop forever
    while running:
        try:
            temperature_celsius, humidity, pressure, timestamp_tz, temperature_fahrenheit = Read_Sensors(bus, address, calibration_params)
            
            lastTemps, trueTemperature = GetTrueTemperature(temperature_fahrenheit, lastTemps)

            currentTime = datetime.datetime.now()

            targetTemp = currentSchedule.get_target_temperature(currentTime)

            if timeTurnedOff is not None:
                timeSinceOff = (datetime.datetime.now() - timeTurnedOff).total_seconds()
            else:
                timeSinceOff = None

            if timeTurnedOn is not None:
                timeSinceOn = (datetime.datetime.now() - timeTurnedOn).total_seconds()
            else:
                timeSinceOn = None

            # within the target range, do nothing
            if targetTemp - 2 <= trueTemperature <= targetTemp + 2:
                pass

            # above target temp, turn off pellet stove
            elif trueTemperature > targetTemp + 2 and pellletStoveState == True:
                if timeSinceOn is None or timeSinceOn >= 90*60:  # 90 minute delay after turning on
                    timeTurnedOff = datetime.datetime.now()
                    pellletStoveState = TurnPelletStoveOn(gpio, False)
            
            # below target temp, turn on pellet stove
            elif trueTemperature < targetTemp - 2 and pellletStoveState == False:
                if timeSinceOff is None or timeSinceOff >= 60*60:  # 60 minute delay after turning off
                    timeTurnedOn = datetime.datetime.now()
                    pellletStoveState = TurnPelletStoveOn(gpio, True)

            # if trueTemperature < targetTemp - 2:
            #     if pellletStoveState == False:
            #         if timeSinceOff is None or timeSinceOff >= 60*60:  # 60 minute delay after turning off
            #             timeTurnedOn = datetime.datetime.now()
            #             pellletStoveState = TurnPelletStoveOn(gpio, True)
                
            # elif trueTemperature > targetTemp + 2:
            #     if pellletStoveState == True:
            #         if timeSinceOn is None or timeSinceOn >= 90*60:  # 90 minute delay after turning on
            #             timeTurnedOff = datetime.datetime.now()
            #             pellletStoveState = TurnPelletStoveOn(gpio, False)
            
            # Print the readings
            print(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + " Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%, Pressure={3:0.2f}hPa".format(temperature_celsius, temperature_fahrenheit, humidity, pressure))
            print('Pellet Stove State = ' + pellletStoveState + " Time since turned on: " + str(timeSinceOn / 60) + " minutes, Time since turned off: " + str(timeSinceOff / 60) + " minutes")

            if __debug__:
                # Save time, date, temperature, humidity, and pressure in .txt file
                file.write(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + ', {:.2f}, {:.2f}, {:.2f}, {:.2f}\n'.format(temperature_celsius, temperature_fahrenheit, humidity, pressure))
                pellletStoveState = TurnPelletStoveOn(gpio, True)
                time.sleep(3)
                pellletStoveState = TurnPelletStoveOn(gpio, False)
                time.sleep(3)
            else:
                time.sleep(60)  # wait for 1 minute before next reading

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
