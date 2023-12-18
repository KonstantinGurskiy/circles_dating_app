from datetime import datetime, timedelta

def check_timer(current_datetime_str):
    # Add the specified hours to the input datetime
    new_datetime = datetime.strptime(current_datetime_str, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)

    # Get the current datetime
    current_datetime = datetime.now()

    # Compare the datetimes
    return new_datetime > current_datetime
