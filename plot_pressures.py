import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# CSV file to read from
filename = "pressure_readings.csv"

# Initialize data storage for plotting
timestamps = []
pressure_data = {i: [] for i in range(1, 7)}

# Read data from the CSV file
with open(filename, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        timestamp = datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S")
        channel = int(row["Channel"])
        pressure = float(row["Pressure"])
        
        timestamps.append(timestamp)
        pressure_data[channel].append(pressure)

# Setup the plot
fig, axes = plt.subplots(6, 1, figsize=(10, 12), sharex=True)
fig.suptitle('Pressure Readings Over Time')

for i, ax in enumerate(axes, start=1):
    ax.plot(timestamps[i-1::6], pressure_data[i], label=f'Ch {i} Pressure', marker='.', color='r', alpha=0.6)
    ax.set_ylabel(f'Ch {i} Pressure')
    ax.grid(True)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    # ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
    # ax.xaxis.set_minor_locator(mdates.SecondLocator(interval=30))
    ax.relim()
    ax.autoscale_view()

# Format the x-axis to improve readability
plt.gcf().autofmt_xdate()
plt.xlabel('Time')
plt.show()
