#!/usr/bin/env python3

import time
import requests
import sys

def process_line(line):
    # Extract the time and the accuracy results
    time_str, data_str = line.split(" // Result is ")

    # Convert the time to a Unix timestamp (use today's date)
    today = time.strftime("%Y-%m-%d")
    log_time = f"{today} {time_str}"
    timestamp = int(time.mktime(time.strptime(log_time, "%Y-%m-%d %H:%M:%S")) * 1e9)

    # Extract values
    line_protocol = f"probe {data_str} {timestamp}"
    
    return line_protocol


for line in sys.stdin:
    line = line.strip()
    if line:  # Skip empty lines
        line_protocol = process_line(line)
        print(f"{line_protocol}")

