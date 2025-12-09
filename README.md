# Vacuum Monitor

Code for reading and displaying the pressures in the experimental chamber.  
The setup polls six gauge channels over a serial connection, writes the values to a CSV file, and produces updated plots for different time windows. A small HTTP server is used to view the plots in a browser.

## What it does

* talks to the pressure controller over `/dev/ttyUSB0`
* logs timestamped pressure readings into `pressure_readings.csv`
* generates rolling plots (minute, hour, day, week, etc.) and per-channel views
* saves a simple status page with the latest values
* serves the output through `python3 -m http.server`

## Running the monitor

python monitor_pressures.py


This collects data continuously and appends it to the CSV file.

## Generating plots

python app.py


This reads the CSV, updates all plots in the `PLOTS/` directory, and refreshes them in a loop.

## Viewing the results

python3 -m http.server 8080



Open `http://localhost:8080` to see the images update as new data arrives.

## Notes

This code was written to keep track of pressures during long experimental runs and to catch sudden changes in the chamber. It is lightweight and designed around the hardware layout with six channels.
