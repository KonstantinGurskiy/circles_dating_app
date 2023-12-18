from datetime import datetime, timedelta

# Define the function to check if the current time is greater than the target time
def check_timer(current_time_str):
    # Add the specified hours to the input time
    new_time = datetime.strptime(current_time_str, "%H:%M:%S") + timedelta(hours=1)

    # Get the current time
    current_time = datetime.now().time()
    # Compare the times
    return new_time.time() > current_time

