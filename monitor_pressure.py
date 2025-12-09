import serial.tools.list_ports as port_list
import serial
from time import sleep, strftime, time
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import numpy as np 


plotting = False
fresh = False



# CSV file to read from and append to
filename = "pressure_readings.csv"

# Initialize data storage for plotting
timestamps = []
pressure_data = {i: [] for i in range(1, 7)}



# Load existing CSV data if file exists
if os.path.exists(filename):
    f = open(filename, "r+")
    lines = f.readlines()
    for i in range(((len(lines)-1)%6)):
        print("pop")
        lines.pop()
    f = open(filename, "w+")
    f.writelines(lines)
    f.close()

    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            print(i)
            timestamp = datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S")
            channel = int(row["Channel"])
            pressure = float(row["Pressure"])
            timestamps.append(timestamp)
            pressure_data[channel].append(pressure)
else:
    # If file does not exist, create a new one with the header
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Channel", "Pressure"])


timestamps = timestamps[::6]


if fresh:
    # Initialize data storage for plotting
    timestamps = []
    pressure_data = {i: [] for i in range(1, 7)}


# List available ports
ports = list(port_list.comports())
for p in ports:
    print(p)

# Open the serial port
ser = serial.Serial('/dev/ttyUSB0',  19200, bytesize=8, parity='N', stopbits=1, timeout=0.2)
print(ser.name)  # Check which port was really used
print("open: ", ser.is_open)

# Function to read pressure for a specific channel
def read_pressure(channel):
    command_template = bytearray(b'PR1\r')
    command_template[2] = channel + 48  # Update the channel number
    ser.write(command_template)
    sleep(0.5)
    ser.read(20)  # Clear any preliminary output
    ser.write(b'\x05\x0d')
    sleep(0.5)
    response = ser.read(20).decode('UTF-8').strip()
    pressure_value = response.split(',')[1] if ',' in response else response
    return pressure_value

if plotting:
    # Setup the plot
    fig, axes = plt.subplots(6, 1, figsize=(10, 12), sharex=True)
    fig.suptitle('Pressure Readings Over Time')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    for i, ax in enumerate(axes, start=1):
        ax.set_ylabel(f'Ch {i} Pressure')
        ax.grid(True)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        ax.xaxis.set_minor_locator(mdates.SecondLocator(interval=30))

hs_tag = 0
# Continuous monitoring loop
try:
    while True:
        timestamp = datetime.now()
        timestamps.append(timestamp)
        
        for s in range(1, 7):
            pressure = read_pressure(s)
            pressure_data[s].append(float(pressure))
            os.system('cls' if os.name == 'nt' else 'clear')
            print("PRESSURE MONITOR")
            print("."*7 + "-"*s + "."*(7-s) + "."*7)
            print(f"Last updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            if hs_tag != 0: #in case the file is empty
                for st in range(1, 7):
                    print(f"Pressure Ch. {st}: {pressure_data[st][-1]:.3E}")

            print("\nFor pressure history run the plot_pressure.py file.")

            # Save the data to the CSV file
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp.strftime('%Y-%m-%d %H:%M:%S'), s, pressure])
            
            if plotting:
                # Update the corresponding subplot
                axes[s-1].cla()
                axes[s-1].plot(timestamps, pressure_data[s], label=f'Ch {s} Pressure', color='r', alpha=0.65)
                axes[s-1].relim()
                axes[s-1].autoscale_view()
                axes[s-1].ticklabel_format(style='sci', axis='y', scilimits=(0,0))

                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

        
        if plotting:
            # Adjust x-axis to show the latest time range
            plt.gcf().autofmt_xdate()
            plt.pause(0.1)  # Pause to update the plot
            plt.savefig("data_pressure_serial/pressures.png")
        # Wait before taking the next set of readings (adjust as needed)
        # sleep(2)
        hs_tag += 1

except KeyboardInterrupt:
    print("Monitoring stopped by user.")

finally:
    ser.close()
    print("Serial port closed.")
    if plotting:
        plt.show()  # Show the final plot when the monitoring stops
