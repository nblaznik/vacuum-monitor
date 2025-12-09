import serial

# Replace '/dev/ttyUSB0' with your actual serial port
ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

# Check if the serial port is open
if ser.is_open:
    print(f"Connected to {ser.name}")

# Write command to request data from the device
# The actual command depends on the device's protocol.
# For example, to get the pressure readings:
ser.write(b'PR1\r\n')  # Example command to read pressure from channel 1

# Read the response from the device
response = ser.readline().decode('ascii').strip()

# Close the serial connection
ser.close()

# Print the received pressure value
print(f"Pressure Reading: {response}")

