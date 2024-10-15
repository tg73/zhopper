#!/usr/bin/env python3
import asyncio
import websockets
import json
from datetime import datetime

# WebSocket URL for Moonraker on ratos2.local
MOONRAKER_WS_URL = "ws://ratos2.local:7125/websocket"

async def subscribe_to_temperatures():
    async with websockets.connect(MOONRAKER_WS_URL) as websocket:
        # Subscribe to temperature updates for the bed and extruder
        subscription_message = {
            "jsonrpc": "2.0",
            "method": "printer.objects.subscribe",
            "params": {
                "objects": {
                    "heater_bed": ["temperature", "target"],
                    "extruder": ["temperature", "target"]
                }
            },
            "id": 1
        }
        await websocket.send(json.dumps(subscription_message))

        while True:
            # Receive and handle messages
            message = await websocket.recv()
            data = json.loads(message)

            # Check if the message is a status update notification
            if data.get("method") == "notify_status_update" and "params" in data:
                # Extract the status data from params
                status_data = data["params"][0] if isinstance(data["params"][0], dict) else {}

                # Extract bed and extruder data if available
                heater_bed_data = status_data.get("heater_bed", {})
                extruder_data = status_data.get("extruder", {})

                # Extract temperature data with fallback to None for each
                bed_temp = heater_bed_data.get("temperature")
                bed_target = heater_bed_data.get("target", 0.0)
                extruder_temp = extruder_data.get("temperature")
                extruder_target = extruder_data.get("target", 0.0)

                # Format available data for InfluxDB line protocol
                timestamp = int(datetime.now().timestamp() * 1e9)
                line_parts = ["temperature,device=3d_printer"]

                if bed_temp is not None:
                    line_parts.append(f"bed_temp={bed_temp},bed_target={bed_target}")
                if extruder_temp is not None:
                    line_parts.append(f"extruder_temp={extruder_temp},extruder_target={extruder_target}")

                # Join the parts and add timestamp
                if len(line_parts) > 1:
                    line = " ".join([",".join(line_parts), str(timestamp)])
                    print(line)
                else:
                    print("Warning: Temperature data is incomplete.")
            else:
                print("Skipping non-status-update message.")

async def main():
    await subscribe_to_temperatures()

# Run the main function
asyncio.run(main())