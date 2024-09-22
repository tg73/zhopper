#!/usr/bin/env python3

import configparser
import os
import requests
import sys
import argparse

# Parse command-line arguments for the bucket name, config file, and config profile
parser = argparse.ArgumentParser(description="Send line protocol data to InfluxDB")
parser.add_argument('--bucket', required=True, help='The InfluxDB bucket to write data to')
parser.add_argument('--config-file', default=os.path.expanduser('~/.influxdbv2/configs'),
                    help='Path to the INI config file (default: ~/.influxdbv2/configs)')
parser.add_argument('--config-name', default='onboarding', 
                    help='Configuration profile name in the INI file (default: onboarding)')
args = parser.parse_args()

# Function to strip surrounding double quotes from a string
def strip_quotes(value):
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value

# Get the config file and config profile from the command-line argument or default values
config_file_path = args.config_file
config_name = args.config_name

# Initialize the configparser and read the INI file
config = configparser.ConfigParser()
config.read(config_file_path)

if config_name in config:
    url = strip_quotes(config[config_name].get("url"))
    token = strip_quotes(config[config_name].get("token"))
    org = strip_quotes(config[config_name].get("org"))
else:
    raise ValueError(f"Configuration '{config_name}' not found in {config_file_path}")

# Get the bucket from the command-line argument
bucket = args.bucket

# Prepare the HTTP request details
precision = "ns"  # Precision for the timestamp (can be ns, ms, s, etc.)
write_url = f"{url}/api/v2/write?org={org}&bucket={bucket}&precision={precision}"

# Set up the HTTP headers
headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "text/plain; charset=utf-8"
}

# Read line protocol data from standard input and send it to InfluxDB
for line in sys.stdin:
    data = line.strip()  # Line protocol data from stdin
    if data:  # Only send non-empty lines
        response = requests.post(write_url, headers=headers, data=data)

        # Check the response
        if response.status_code == 204:
            print(f"Wrote: {data}", flush=True)
        else:
            print(f"Failed to write data: {response.status_code}, {response.text}")