import threading
import time
from DeviceControl import Read_Sensors, TurnPelletStoveOn, initialize_Sensors, GetTrueTemperature
import Schedule
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os
from typing import List, Tuple

class ThermostatGUI:

    def __init__(self):
        self.running = False
        self.refresh_thread = None

        # Create main window
        self.root = tk.Tk()
        self.root.title("Thermostat Control")
        self.root.geometry("1200x800")

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.setup_gui()
        self.start_auto_refresh()
        

    def setup_gui(self):
        """Set up the GUI layout."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Thermostat Control Dashboard",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Left panel - Current data
        self.setup_current_data_panel(main_frame)

    def setup_current_data_panel(self, parent):
        """Set up the current weather data display panel."""
        # Current weather frame
        current_frame = ttk.LabelFrame(parent, text="Current Weather", padding="10")
        current_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        # Weather data labels
        self.weather_vars = {}
        weather_fields = [
            ("Temperature", "°F"),
            ("Humidity", "%"),
            ("Pressure", "hPa"),
        ]

        for i, (field, unit) in enumerate(weather_fields):
            # Field label
            label = ttk.Label(current_frame, text=f"{field}:", font=('Arial', 10, 'bold'))
            label.grid(row=i, column=0, sticky=tk.W, pady=2)

            # Value variable and label
            var = tk.StringVar(value="--")
            self.weather_vars[field.lower().replace(" ", "_")] = var

            value_label = ttk.Label(current_frame, textvariable=var, font=('Arial', 10))
            value_label.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)

            # Unit label
            if unit:
                unit_label = ttk.Label(current_frame, text=unit, font=('Arial', 10))
                unit_label.grid(row=i, column=2, sticky=tk.W, padx=(5, 0), pady=2)

        # Statistics frame
        stats_frame = ttk.LabelFrame(current_frame, text="Database Statistics", padding="5")
        stats_frame.grid(row=len(weather_fields), column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        self.stats_vars = {}
        stats_fields = ["Total Weather Records", "Total Flux Records", "Database Size"]

        for i, field in enumerate(stats_fields):
            label = ttk.Label(stats_frame, text=f"{field}:", font=('Arial', 9))
            label.grid(row=i, column=0, sticky=tk.W, pady=1)

            var = tk.StringVar(value="--")
            self.stats_vars[field.lower().replace(" ", "_")] = var

            value_label = ttk.Label(stats_frame, textvariable=var, font=('Arial', 9))
            value_label.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=1)

    def start_auto_refresh(self):
        """Start the auto-refresh thread."""
        self.running = True
        self.refresh_thread = threading.Thread(target=self.auto_refresh_worker, daemon=True)
        self.refresh_thread.start()

        # Initial data load
        self.refresh_data()

    def auto_refresh_worker(self):
        """Worker thread for auto-refresh."""
        while self.running:
            time.sleep(30)  # Refresh every 30 seconds
            if self.running and self.auto_refresh_var.get():
                try:
                    # Only auto-refresh if not using custom range
                    # Custom ranges should be manually refreshed
                    if not self.use_custom_range:
                        # Schedule refresh in main thread
                        self.root.after(0, self.refresh_data)
                    else:
                        # Just update current weather data, not charts
                        self.root.after(0, self.update_current_weather)
                        self.root.after(0, self.update_statistics)
                except:
                    break

    def on_closing(self):
        """Handle window closing."""
        self.running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=1)
        self.root.destroy()

    def refresh_data(self):
        """Refresh all data in the GUI."""
        

    def run(self):
        """Run the GUI application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Weather Station Tkinter GUI")
    parser.add_argument("--db", default="weather_data.db",
                        help="Database file path (default: weather_data.db)")

    args = parser.parse_args()

    try:
        app = WeatherGUI(args.db)
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start GUI: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()