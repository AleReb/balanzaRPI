from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas
import asyncio
import websockets
import serial
import time
import webbrowser

# Initialize variables
device = None

# Attempt to initialize the OLED
try:
    # I2C serial configuration
    seriali2c = i2c(port=1, address=0x3C)  # Common I2C address for SH1106
    device = sh1106(seriali2c)
    
    # Display initial message on OLED
    with canvas(device) as draw:
        draw.text((0, 0), "Start Script", fill="white")
except Exception as e:
    print(f"Failed to initialize OLED: {e}")
    device = None  # Ensure the device is set to None if initialization fails

# Configure the serial port and baud rate
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)  # Change '/dev/ttyAMA0' if you use another port
# Wait for the server to start
time.sleep(2)

# Open the default web browser to the URL
webbrowser.open("http://localhost:8000/index.html?x0=253&x1=29&y0=177&y1=247&invert=false&gamma=0.8&skew=1&vskew=0&gap=10&format=8.8.8.8.8&interval=500")

async def handle_connection(websocket, path):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Message received from client: {message}")

            # Extract only the numeric part before any whitespace
            data_to_send = message.split()[0]  # Gets only the first part (number)

            # Update OLED display if available
            if device:
                try:
                    with canvas(device) as draw:
                        draw.text((0, 0), "Received:", fill="white")
                        draw.text((0, 20), data_to_send, fill="white")  # Second line with the received data
                except Exception as e:
                    print(f"Error updating OLED: {e}")

            # Write the numeric part to the serial port
            ser.write((data_to_send + '\n').encode('utf-8'))  # Add newline character and encode to bytes  # Convert to bytes for serial transmission
            
            time.sleep(0.1)
            # Send response back to the WebSocket client
            response = f"Processed: {data_to_send}"
            await websocket.send(response)
            
            # Read response from the serial port in bytes
            serial_response = ser.readline().decode('utf-8').strip()
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
