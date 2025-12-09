import serial.tools.list_ports as port_list
import serial
from time import sleep, strftime, time
import csv

# List available ports
ports = list(port_list.comports())
for p in ports:
    print(p)

# Open the serial port
ser = serial.Serial('/dev/ttyUSB0', 19200, bytesize=8, parity='N', stopbits=1, timeout=0.2)
print(ser.name)  # Check which port was really used
print("open: ", ser.is_open)

# CSV file setup
filename = "pressure_readings.csv"
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Channel", "Pressure"])

# Function to read pressure for a specific channel
def read_pressure(channel):
    command_template = bytearray(b'PR1\r')
    command_template[2] = channel + 48  # Update the channel number
    ser.write(command_template)
    sleep(0.5)
    ser.read(10)  # Clear any preliminary output
    ser.write(b'\x05\x0d')
    sleep(0.5)
    response = ser.read(10).decode('UTF-8').strip()
    pressure_value = response.split(',')[1] if ',' in response else response
    return pressure_value

# Continuous monitoring loop
try:
    while True:
        timestamp = strftime("%Y-%m-%d %H:%M:%S")
        for s in range(1, 7):
            pressure = read_pressure(s)
            print(f"{timestamp} - Pressure Ch. {s}: {pressure}")
            
            # Save the data to the CSV file
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, s, pressure])
        
        # Wait before taking the next set of readings (adjust as needed)
        sleep(2)

except KeyboardInterrupt:
    print("Monitoring stopped by user.")

finally:
    ser.close()
    print("Serial port closed.")
