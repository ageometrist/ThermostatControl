import datetime

class Schedule:
    def __init__(self):
        self.schedule = {}  # Dictionary to hold schedule data

    def add_schedule(self, day_of_week, start_time, end_time, target_temperature):
        """Add a schedule entry for a specific day of the week."""
        if day_of_week not in self.schedule:
            self.schedule[day_of_week] = []
        self.schedule[day_of_week].append({
            'start_time': start_time,
            'end_time': end_time,
            'target_temperature': target_temperature
        })

    def get_target_temperature(self, current_datetime: datetime.datetime):
        """Get the target temperature based on the current date and time."""
        day_of_week = current_datetime.weekday # Get the day of the week
        current_time = current_datetime.time() # Get the current time

        # Check the schedule for the current day
        if day_of_week in self.schedule:
            for entry in self.schedule[day_of_week]:
                if entry['start_time'] <= current_time <= entry['end_time']:
                    return entry['target_temperature']
                
        return 61  #  default temperature if no schedule matches