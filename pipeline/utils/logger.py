import datetime
"""
This will be passed wherever we want to print a message
during the pipeline stages
"""
def log(message  : str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}]:  {message}")