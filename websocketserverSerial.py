import asyncio
import websockets
import serial
import time
import webbrowser
import os
#file:///home/pi/7seg-ocr/index.html?x0=98&x1=305&y0=69&y1=135&invert=false&gamma=4&skew=-1&vskew=-1.5&gap=13&format=8.8.8.8.8&interval=30
#http://localhost:8000/index.html?x0=13&x1=249&y0=76&y1=151&invert=false&gamma=4&skew=2&vskew=0&gap=10&format=8.8.8.8.8&interval=100
# Configure the serial port and baud rate
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)  # Change '/dev/ttyAMA0' if you use another port
# Wait for the server to start
time.sleep(2)

# Open the default web browser to the URL
webbrowser.open("http://localhost:8000/index.html?x0=13&x1=249&y0=76&y1=151&invert=false&gamma=4&skew=2&vskew=0&gap=10&format=8.8.8.8.8&interval=100")

async def handle_connection(websocket, path):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Message received from client: {message}")
            
            # Extract only the numeric part before any whitespace
            data_to_send = message.split()[0]  # Gets only the first part (number)
            
            # Write the numeric part to the serial port
            ser.write(data_to_send.encode('utf-8'))  # Convert to bytes for serial transmission
            time.sleep(0.1)
            # Send response back to the WebSocket client
            response = f"Processed: {data_to_send}"
            await websocket.send(response)
            
            # Read response from the serial port in bytes
            serial_response = ser.readline()
            if serial_response:
                print("Received from serial:", serial_response)
                
            # Optional: Add a slight delay to manage frequency
            await asyncio.sleep(1)
    except websockets.ConnectionClosed:
        print("Connection closed")
    finally:
        print("Client disconnected")

async def main():
    async with websockets.serve(handle_connection, "127.0.0.1", 8181):
        print("WebSocket server started at ws://127.0.0.1:8181")
        await asyncio.Future()  # Run indefinitely

# Check if an event loop is already running
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "already running" in str(e):
            loop = asyncio.get_running_loop()
            loop.create_task(main())
        else:
            raise e
