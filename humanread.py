#!/usr/bin/env python3
import sys
import re
import argparse
from datetime import datetime

def parse_line_protocol(line, format):
    # Example line format: measurement,tag key1=value1,key2=value2 timestamp
    pattern = r'(?P<measurement>[\w_]+)(?:,(?P<tag>[\w=]+))? (?P<fields>.+) (?P<timestamp>\d+)$'
    match = re.match(pattern, line)
    
    if not match:
        return None

    # Parse components
    measurement = match.group('measurement')
    tag = match.group('tag')
    timestamp = match.group('timestamp')
    
    # Parse fields into a dictionary
    fields = match.group('fields')
    field_data = {}
    
    for field in fields.split(','):
        key, value = field.split('=')
        try:
            # Try to format as a float with up to 3 decimal places, preserving original format
            float_value = float(value)
            if float_value.is_integer():
                # If the value is an integer, show it without decimals
                field_data[key] = f"{int(float_value)}"
            else:
                # Only display up to 3 necessary decimal places
                field_data[key] = f"{float_value:.3f}".rstrip('0').rstrip('.')
        except ValueError:
            # If not a float, keep as-is
            field_data[key] = value

    # Convert timestamp to a human-readable format
    readable_timestamp = \
        datetime.fromtimestamp(int(timestamp) / 1e9).strftime('%Y-%m-%d %H:%M:%S') if format == 'line' \
            else datetime.fromtimestamp(int(timestamp) / 1e9).isoformat()
    
    return {
        'measurement': measurement,
        'tag': tag,
        'fields': field_data,
        'timestamp': readable_timestamp
    }

def display_header(fields, format):
    if format == "line":
        # Create the header with dynamic field names
        header = f"{'Timestamp':<20} {'Measurement':<15} {'Tag':<20}"
        for field in sorted(fields):
            header += f"{field:<15}"
        print(header, flush=True)
        print("=" * len(header), flush=True)
    elif format == 'csv':
        header_parts = ['timestamp', 'measurement']
        header_parts.extend(map(lambda f: f if not " " in f else '"' + f + '"', sorted(fields)))
        header = ",".join(header_parts)
        print(header, flush=True)

def display_entry(entry, fields, format):
    if format == "line":
        # Ensure columns for all known fields, leaving space for missing fields
        field_values = []
        for field in sorted(fields):
            value = entry['fields'].get(field, "")
            field_values.append(f"{value:<15}")

        line = f"{entry['timestamp']:<20} {entry['measurement']:<15} {entry['tag'] or '':<20}" + "".join(field_values)
        print(line, flush=True)
    elif format == "csv":
        values = [entry['timestamp'],entry['measurement']]
        values.extend(map(lambda f: entry['fields'].get(f,""), sorted(fields)))
        line = ",".join(values)
        print(line, flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate time-weighted averages from InfluxDB line protocol input.")
    parser.add_argument("--format", choices=["csv", "line"], default="line", help="Output format: 'csv' or 'line' protocol (default: 'line').")
    args = parser.parse_args()
    
    parsed_data = []
    all_fields = set()  # Tracks all unique field names seen
    
    # Read input line by line
    for line in sys.stdin:
        line = line.strip()
        parsed_entry = parse_line_protocol(line, args.format)
        if parsed_entry:
            # Track fields to maintain consistent columns
            current_fields = set(parsed_entry['fields'].keys())
            new_fields = current_fields - all_fields
            all_fields.update(current_fields)

            # Display the header again if new fields are added
            if new_fields:
                display_header(all_fields, args.format)

            # Display each entry, filling in blanks for missing fields
            display_entry(parsed_entry, all_fields, args.format)

            # Store the parsed entry for potential further processing
            parsed_data.append(parsed_entry)