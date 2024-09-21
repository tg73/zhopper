#!/usr/bin/env python3

import time
import requests
import sys

def process_line(line):
    # Extract the time and the accuracy results
    time_str, data_str = line.split(" // probe accuracy results: ")

    # Convert the time to a Unix timestamp (use today's date)
    today = time.strftime("%Y-%m-%d")
    log_time = f"{today} {time_str}"
    timestamp = int(time.mktime(time.strptime(log_time, "%Y-%m-%d %H:%M:%S")) * 1e9)

    # Extract values
    data = data_str.strip().split(", ")
#    print (data)
    data_dict = {}
    for item in data:
        key, value = item.rsplit(" ", 1)
        value = float(value)
        key = key.replace("standard deviation", "stddev")
        data_dict[key] = value

    # Prepare Line Protocol format
    fields = ",".join([f"{key}={value}" for key, value in data_dict.items()])
    line_protocol = f"probe_accuracy {fields} {timestamp}"
    
    return line_protocol


for line in sys.stdin:
    line = line.strip()
    if line:  # Skip empty lines
        line_protocol = process_line(line)
        print(f"{line_protocol}")

