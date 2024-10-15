#!/usr/bin/env python3
import asyncio
import websockets
import json
import argparse
from datetime import datetime

async def listen_temperatures(host="localhost", objects=None):
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
                timestamp = int(datetime.now().timestamp() * 1e9)
                line_parts = ["temperature,device=3d_printer"]

                # Loop over each object to extract temperature, target, and PWM data
                for obj in objects:
                    obj_data = status_data.get(obj, {})
                    temp = obj_data.get("temperature")
                    target = obj_data.get("target", 0.0)
                    pwm = obj_data.get("power", 0.0)
                    
                    # Append object data if temperature is available
                    if temp is not None:
                        line_parts.append(f"{obj}_temp={temp},{obj}_target={target},{obj}_pwm={pwm}")

                # Join the parts and print if any data is present
                if len(line_parts) > 1:
                    line = " ".join([",".join(line_parts), str(timestamp)])
                    print(line, flush=True)
                else:
                    print("Warning: Temperature data is incomplete.", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Listen for temperature and PWM data from Moonraker.")
    parser.add_argument("--host", required=True, help="Hostname or IP address of the Moonraker server.")
    parser.add_argument("--obj", required=True, nargs='+', help="Objects to monitor (e.g., heater_bed extruder).")
    
    # Parse arguments
    args = parser.parse_args()

    # Run the WebSocket listener
    asyncio.run(listen_temperatures(host=args.host, objects=args.obj))