import cv2
import pytesseract
from matplotlib import pyplot as plt
from datetime import datetime
import time 
from PIL import Image
import matplotlib.dates as mdates
import os
import numpy as np
import re
from scipy.signal import savgol_filter

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
os.system('clear')

def clear_terminal():
    """Clear the terminal screen."""
    os.system('clear')

def list_files(directory):
    """List all .npy files in the directory and extract dates from filenames."""
    files = os.listdir(directory)
    date_pattern = re.compile(r"times_(\d{8})\.npy")
    dates = [date_pattern.search(file).group(1) for file in files if date_pattern.search(file)]
    return dates

def extract_date_components(dates):
    """Extract unique years, months, and days from the list of dates."""
    years = sorted(set(date[:4] for date in dates))
    months = sorted(set(date[4:6] for date in dates))
    days = sorted(set(date[6:] for date in dates))
    return years, months, days

def user_select(options, prompt):
    """Display options and prompt user to select one."""
    for i, option in enumerate(options, 1):
        print(f"{i}: {option}")
    while True:
        user_input = input(prompt).strip()
        if user_input == "":  # If user presses Enter without input
            return options[0]  # Automatically select the first option
        try:
            choice = int(user_input)
            if 1 <= choice <= len(options):
                return options[choice - 1]
        except ValueError:
            pass
        print("Invalid choice, please try again.")

def main(directory):
    # Step 1: List all dates from files
    dates = list_files(directory)
    
    # Step 2: Extract unique years, months, and days
    years, _, _ = extract_date_components(dates)
    
    # Step 3: User selects a year
    clear_terminal()
    print("Select a year:")
    selected_year = user_select(years, "Enter the number of the desired year (or press Enter to select the first option): ")
    
    # Filter dates by the selected year
    filtered_dates = [date for date in dates if date.startswith(selected_year)]
    
    # Step 4: Extract months from the filtered dates
    clear_terminal()
    _, months, _ = extract_date_components(filtered_dates)
    print("Select a month:")
    selected_month = user_select(months, "Enter the number of the desired month (or press Enter to select the first option): ")
    
    # Further filter dates by the selected month
    filtered_dates = [date for date in filtered_dates if date.startswith(selected_year + selected_month)]
    
    # Step 5: Extract days from the filtered dates
    clear_terminal()
    _, _, days = extract_date_components(filtered_dates)
    print("Select a day:")
    selected_day = user_select(days, "Enter the number of the desired day (or press Enter to select the first option): ")
    
    # Final selected date
    clear_terminal()
    selected_date = selected_year + selected_month + selected_day
    print(f"You have selected the date: {selected_date}")
    return selected_date


# Directory containing the files
directory = "data_pressure"
date = main(directory)
s_path_time = f"data_pressure/times_{date}.npy"
s_path_pressure = f"data_pressure/pressure_{date}.npy"

if os.path.exists(s_path_time) and os.path.exists(s_path_pressure):
    times = np.load(s_path_time, allow_pickle=True).tolist()
    pressures = np.load(s_path_pressure, allow_pickle=True).tolist()


# This I think is if the code is (somehow) interrupted just between the savings. 
if len(times) > len(pressures):
    times = times[:len(pressures)]

elif len(times) < len(pressures):
    pressures = pressures[:len(times)]

#np.save(f"data_pressure/times_{old_date}", times)
#np.save(f"data_pressure/pressure_{old_date}", pressures)




fig, ax = plt.subplots()
ax.plot(times, pressures, 'r-', alpha=0.3)
ax.plot(times, savgol_filter(pressures, window_length=max(3, len(pressures)//100), polyorder=2), 'g-', alpha=0.6)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Set x-axis format to HH:MM
plt.xlabel("Time (HH:MM)")
ax.set_xlabel('Time')
ax.set_ylabel('Pressure (mbar)')
ax.set_title(f'Pressure - {date}')
plt.gcf().autofmt_xdate()  # Auto-format date on the x-axis
plt.show()
