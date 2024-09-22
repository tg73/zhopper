#!/usr/bin/env python3

import time
import sys
import argparse
from datetime import datetime

def process_line(line, *, result_header, measurement, tag=None):
    # Extract the time and the accuracy results
    try:
        time_str, data_str = line.split(result_header)
    except ValueError:
        print(f"Line does not contain the result header: {line}", file=sys.stderr)
        return None

    timestamp = time_str.strip()
    try:
        # Convert the timestamp to a Unix timestamp in nanoseconds
        timestamp_ns = int(time.mktime(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").timetuple()) * 1e9)
    except ValueError:
        print(f"Invalid timestamp format: {timestamp}", file=sys.stderr)
        return None

    # Extract values
    # Split the data based on commas and strip any leading/trailing spaces
    data = [item.strip() for item in data_str.split(",")]
    data_dict = {}
    for item in data:
        try:
            splitter = "=" if "=" in item else " " #key and value can be separated by a space or an equal sign
            key, value = item.rsplit(splitter, 1)
            value = float(value)
            key = key.replace(" ", "_")  # Replace all spaces with underscores in the field keys
            data_dict[key] = value
        except ValueError:
            print(f"Skipping malformed data: {item}", file=sys.stderr)
            continue

    # Prepare Line Protocol format using the provided measurement and optional tag
    fields = ",".join([f"{key}={value}" for key, value in data_dict.items()])
    
    # If a tag is provided, add it to the line protocol
    tag_part = f",{tag}" if tag else ""
    
    line_protocol = f"{measurement}{tag_part} {fields} {timestamp_ns}"
    
    return line_protocol

# Set up argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="Process log lines and convert them to InfluxDB line protocol.")
    parser.add_argument("--result-header", required=True, help="The header used to split the log line and extract results.")
    parser.add_argument("--measurement", required=True, help="The measurement name to use in the InfluxDB line protocol.")
    parser.add_argument("--tag", help="Optional tag in the format key=value to add to the InfluxDB line protocol.")
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Read lines from stdin
    for line in sys.stdin:
        line = line.strip()
        if args.result_header in line:  # Only process lines with the correct format
            try:
                line_protocol = process_line(line, result_header=args.result_header, measurement=args.measurement, tag=args.tag)
                if line_protocol:
                    print(f"{line_protocol}", flush=True)
            except ValueError:
                # Handle case where the split or conversion fails, if necessary
                print(f"Skipping malformed line: {line}", file=sys.stderr)

if __name__ == "__main__":
    main()