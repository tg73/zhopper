import asyncio
import websockets
import json
import argparse

async def listen_gcode_responses(host="localhost"):
    uri = f"ws://{host}/websocket"  # Replace <moonraker-ip> with your Moonraker server's IP
    async with websockets.connect(uri) as websocket:
        # Continuously listen for G-code responses (notify_gcode_response)
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            
            # Check if the message contains G-code response
            if data.get("method") == "notify_gcode_response":
                gcode_response = data.get("params", [])[0]
                print(f"G-code Response: {gcode_response}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Listen for G-code responses from Moonraker.")
    parser.add_argument("--host", required=True, help="Hostname or IP address of the Moonraker server.")    
    # Parse arguments
    args = parser.parse_args()
    

# Run the WebSocket listener

asyncio.run(listen_gcode_responses(host=args.host))