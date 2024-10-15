#!/usr/bin/env python3
import asyncio
import websockets
import json
import argparse
from datetime import datetime

async def listen_temperatures(host="localhost", objects=None, measurement="temperature", tag=None, output_format="line"):
    uri = f"ws://{host}/websocket"  # Moonraker WebSocket URL
    
    # Build the subscription message with specified objects
    subscription_params = {obj: ["temperature", "target", "power"] for obj in objects}
    subscription_message = {
        "jsonrpc": "2.0",
        "method": "printer.objects.subscribe",
        "params": {
            "objects": subscription_params
        },
        "id": 1
    }

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(subscription_message))

        # Continuously listen for temperature and PWM updates
        while True:
            response = await websocket.recv()
            data = json.loads(response)

            # Process only 'notify_status_update' messages
            if data.get("method") == "notify_status_update":
                status_data = data["params"][0] if isinstance(data["params"][0], dict) else {}
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if output_format == "csv" else int(datetime.now().timestamp() * 1e9)
                
                # Prepare data for the selected format
                if output_format == "line":
                    # Start with the measurement name and optional tag
                    line_parts = [f"{measurement}"]
                    if tag:
                        line_parts[0] += f",{tag}"
                    
                    # Append object data in InfluxDB line protocol format
                    field_parts = []
                    for obj in objects:
                        obj_data = status_data.get(obj, {})
                        temp = obj_data.get("temperature")
                        target = obj_data.get("target", 0.0)
                        pwm = obj_data.get("power", 0.0)
                        
                        if temp is not None:
                            field_parts.append(f"{obj}_temp={temp},{obj}_target={target},{obj}_pwm={pwm}")
                    
                    if field_parts:
                        line = " ".join([",".join(line_parts), ",".join(field_parts), str(timestamp)])
                        print(line, flush=True)
                    else:
                        print("Warning: Temperature data is incomplete.", flush=True)
                
                elif output_format == "csv":
                    # Build CSV format header for timestamp and fields
                    csv_parts = [timestamp]
                    for obj in objects:
                        obj_data = status_data.get(obj, {})
                        temp = obj_data.get("temperature", "")
                        target = obj_data.get("target", "")
                        pwm = obj_data.get("power", "")
                        
                        csv_parts.extend([temp, target, pwm])
                    
                    # Convert list to CSV line and print
                    csv_line = ",".join(map(str, csv_parts))
                    print(csv_line, flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Listen for temperature and PWM data from Moonraker.")
    parser.add_argument("--host", required=True, help="Hostname or IP address of the Moonraker server.")
    parser.add_argument("--obj", required=True, nargs='+', help="Objects to monitor (e.g., heater_bed extruder).")
    parser.add_argument("--measurement", required=True, help="The measurement name to use in the InfluxDB line protocol.")
    parser.add_argument("--tag", help="Optional tag in the format key=value to add to the InfluxDB line protocol.")
    parser.add_argument("--format", choices=["csv", "line"], default="line", help="Output format: 'csv' or 'line' protocol (default: 'line').")
    
    # Parse arguments
    args = parser.parse_args()

    # Run the WebSocket listener
    asyncio.run(listen_temperatures(host=args.host, objects=args.obj, measurement=args.measurement, tag=args.tag, output_format=args.format))