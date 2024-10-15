#!/usr/bin/env python3
import sys
import re
import argparse
from datetime import datetime

def parse_line_protocol(line):
    # Example line format: measurement,tag key1=value1,key2=value2 timestamp
    pattern = r'(?P<measurement>[\w_]+)(?:,(?P<tag>[\w=]+))? (?P<fields>.+) (?P<timestamp>\d+)$'
    match = re.match(pattern, line)
    
    if not match:
        return None

    # Parse components
    measurement = match.group('measurement')
    tag = match.group('tag')
    timestamp = int(match.group('timestamp'))
    fields = match.group('fields')
    field_data = {}
    
    for field in fields.split(','):
        key, value = field.split('=')
        try:
            # Store the value as a float for averaging
            field_data[key] = float(value)
        except ValueError:
            continue  # Ignore non-numeric fields

    return {
        'measurement': measurement,
        'tag': tag,
        'fields': field_data,
        'timestamp': timestamp
    }

def time_weighted_average(values, start_time, interval_ns):
    # Calculate time-weighted averages for each field
    weighted_sums = {}
    weighted_times = {}
    current_time = start_time
    total_duration = interval_ns

    for i in range(1, len(values)):
        field_data = values[i-1]['fields']
        time_diff = values[i]['timestamp'] - values[i-1]['timestamp']
        
        for field, value in field_data.items():
            weighted_sums[field] = weighted_sums.get(field, 0) + value * time_diff
            weighted_times[field] = weighted_times.get(field, 0) + time_diff

        current_time = values[i]['timestamp']

    # Handle the final segment up to the end of the interval
    last_data = values[-1]['fields']
    last_duration = total_duration - (current_time - start_time)
    
    for field, value in last_data.items():
        weighted_sums[field] = weighted_sums.get(field, 0) + value * last_duration
        weighted_times[field] = weighted_times.get(field, 0) + last_duration

    # Compute the average
    averages = {}
    for field, total_weighted_sum in weighted_sums.items():
        averages[field] = total_weighted_sum / weighted_times[field] if weighted_times[field] else 0

    return averages

def format_line_protocol(measurement, tag, averages, timestamp):
    # Format the output in the same line protocol format as the input
    tag_part = f",{tag}" if tag else ""
    field_part = ",".join([f"{field}={value:.3f}".rstrip('0').rstrip('.') for field, value in averages.items()])
    return f"{measurement}{tag_part} {field_part} {timestamp}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate time-weighted averages from InfluxDB line protocol input.")
    parser.add_argument("--interval", type=int, default=10, help="Averaging time period in seconds (default: 10)")
    args = parser.parse_args()
    
    interval_ns = args.interval * 1e9  # Convert interval to nanoseconds
    current_values = []
    start_time = None

    for line in sys.stdin:
        line = line.strip()
        parsed_data = parse_line_protocol(line)
        
        if parsed_data:
            # Initialize start time
            if start_time is None:
                start_time = parsed_data['timestamp']
            
            # Collect values until the interval is reached
            current_values.append(parsed_data)

            # Calculate and display averages when interval is reached
            if parsed_data['timestamp'] - start_time >= interval_ns:
                averages = time_weighted_average(current_values, start_time, interval_ns)
                output_line = format_line_protocol(
                    parsed_data['measurement'],
                    parsed_data['tag'],
                    averages,
                    parsed_data['timestamp']
                )
                print(output_line, flush=True)
                
                # Reset for the next interval
                current_values = [parsed_data]
                start_time = parsed_data['timestamp']