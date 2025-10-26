import os
import time
import pytz
import datetime
import numpy as np
import tkinter as tk
from DeviceControl import Read_Sensors, TurnPelletStoveOn, initialize_Sensors

def GetTrueTemperature(temperature, tempsList: np.ndarray):
    # maintain a rolling list of last 10 temperature readings
    if tempsList.count >= 10:
        tempsList = np.roll(tempsList, -1)
        tempsList[9] = temperature
    else:
        tempsList.append(temperature)

    # compute mean ignoring NaNs (handles initial empty slots)
    float(np.nanmean(tempsList))

    return tempsList, temperature

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

    
    
    # loop forever
    while running:
        try:
            temperature_celsius, humidity, pressure, timestamp_tz, temperature_fahrenheit = Read_Sensors(bus, address, calibration_params)
            
            lastTemps, trueTemperature = GetTrueTemperature(temperature_fahrenheit, lastTemps)


            
            # Print the readings
            print(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + " Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%, Pressure={3:0.2f}hPa".format(temperature_celsius, temperature_fahrenheit, humidity, pressure))

            # Save time, date, temperature, humidity, and pressure in .txt file
            file.write(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + ', {:.2f}, {:.2f}, {:.2f}, {:.2f}\n'.format(temperature_celsius, temperature_fahrenheit, humidity, pressure))
            pellletStoveState = TurnPelletStoveOn(gpio, True)
            time.sleep(3)
            pellletStoveState = TurnPelletStoveOn(gpio, False)
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


# chat gpt version with gui
def __main__():
    bus, address, calibration_params, gpio = initialize_Sensors()

    # Check if the file exists before opening it in 'a' mode (append mode)
    file_exists = os.path.isfile('sensor_readings_bme280.txt')
    file = open('sensor_readings_bme280.txt', 'a')

    # Write the header to the file if the file does not exist
    if not file_exists:
        file.write('Time and Date, temperature (ºC), temperature (ºF), humidity (%), pressure (hPa)\n')

    # initial rolling buffer
    lastTemps = np.full(10, np.nan)
    trueTemperature = None
    pelletStoveState = False

    # --- simple Tkinter GUI to show current temp and set target temp ---
    class ThermostatApp:
        def __init__(self, root):
            self.root = root
            root.title("Thermostat Control")

            # UI variables
            self.current_temp_var = tk.StringVar(value="N/A")
            self.target_temp_var = tk.DoubleVar(value=21.0)  # default setpoint ºC

            # layout
            tk.Label(root, text="Current temperature (ºF):").grid(row=0, column=0, sticky="w", padx=8, pady=6)
            tk.Label(root, textvariable=self.current_temp_var, font=("Helvetica", 14)).grid(row=0, column=1, sticky="e", padx=8, pady=6)

            tk.Label(root, text="Target temperature (ºC):").grid(row=1, column=0, sticky="w", padx=8, pady=6)
            self.scale = tk.Scale(root, from_=5.0, to=35.0, resolution=0.5, orient="horizontal", variable=self.target_temp_var, length=300)
            self.scale.grid(row=1, column=1, padx=8, pady=6)

            self.set_button = tk.Button(root, text="Apply Setpoint", command=self.apply_setpoint)
            self.set_button.grid(row=2, column=0, columnspan=2, pady=(0,10))

            # store objects/state
            self.poll_interval_ms = 3000
            self.lastTemps = lastTemps
            self.trueTemperature = trueTemperature
            self.file = file
            self.bus = bus
            self.address = address
            self.calibration_params = calibration_params
            self.gpio = gpio

            # handle close
            root.protocol("WM_DELETE_WINDOW", self.on_close)

            # start polling sensors
            root.after(100, self.poll_sensors)

        def apply_setpoint(self):
            # currently just prints/applies locally; integration with control logic can be added
            setpoint = self.target_temp_var.get()
            print(f"Setpoint applied: {setpoint:.1f} ºC")

        def poll_sensors(self):
            try:
                temperature_celsius, humidity, pressure, timestamp_tz, temperature_fahrenheit = Read_Sensors(self.bus, self.address, self.calibration_params)

                # update rolling buffer and smoothed value
                self.lastTemps, smoothed_f = GetTrueTemperature(temperature_fahrenheit, self.lastTemps)
                self.trueTemperature = smoothed_f

                # update UI
                self.current_temp_var.set(f"{self.trueTemperature:.1f}")

                # log to file
                self.file.write(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + ', {:.2f}, {:.2f}, {:.2f}, {:.2f}\n'.format(
                    temperature_celsius, temperature_fahrenheit, humidity, pressure))
                self.file.flush()

                # optional: simple control example (comment out if not desired)
                # if temperature_celsius < self.target_temp_var.get():
                #     pelletStoveState = TurnPelletStoveOn(self.gpio, True)
                # else:
                #     pelletStoveState = TurnPelletStoveOn(self.gpio, False)

            except Exception as e:
                print('Sensor read error:', e)

            finally:
                # schedule next poll
                self.root.after(self.poll_interval_ms, self.poll_sensors)

        def on_close(self):
            try:
                self.file.close()
            except Exception:
                pass
            self.root.destroy()

    root = tk.Tk()
    app = ThermostatApp(root)
    root.mainloop()
