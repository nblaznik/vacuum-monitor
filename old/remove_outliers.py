# ## If text recognition acts out, run this script to fix all the outliers. 
# import numpy as np
# import pytesseract
# import os
# import numpy as np
# import re
# os.system('clear')
# def clear_terminal():
#     """Clear the terminal screen."""
#     os.system('clear')

# def list_files(directory):
#     """List all .npy files in the directory and extract dates from filenames."""
#     files = os.listdir(directory)
#     date_pattern = re.compile(r"times_(\d{8})\.npy")
#     dates = [date_pattern.search(file).group(1) for file in files if date_pattern.search(file)]
#     return dates

# def extract_date_components(dates):
#     """Extract unique years, months, and days from the list of dates."""
#     years = sorted(set(date[:4] for date in dates))
#     months = sorted(set(date[4:6] for date in dates))
#     days = sorted(set(date[6:] for date in dates))
#     return years, months, days

# def user_select(options, prompt):
#     """Display options and prompt user to select one."""
#     for i, option in enumerate(options, 1):
#         print(f"{i}: {option}")
#     while True:
#         user_input = input(prompt).strip()
#         if user_input == "":  # If user presses Enter without input
#             return options[0]  # Automatically select the first option
#         try:
#             choice = int(user_input)
#             if 1 <= choice <= len(options):
#                 return options[choice - 1]
#         except ValueError:
#             pass
#         print("Invalid choice, please try again.")

# def main(directory):
#     # Step 1: List all dates from files
#     dates = list_files(directory)
    
#     # Step 2: Extract unique years, months, and days
#     years, _, _ = extract_date_components(dates)
    
#     # Step 3: User selects a year
#     clear_terminal()
#     print("Select a year:")
#     selected_year = user_select(years, "Enter the number of the desired year (or press Enter to select the first option): ")
    
#     # Filter dates by the selected year
#     filtered_dates = [date for date in dates if date.startswith(selected_year)]
    
#     # Step 4: Extract months from the filtered dates
#     clear_terminal()
#     _, months, _ = extract_date_components(filtered_dates)
#     print("Select a month:")
#     selected_month = user_select(months, "Enter the number of the desired month (or press Enter to select the first option): ")
    
#     # Further filter dates by the selected month
#     filtered_dates = [date for date in filtered_dates if date.startswith(selected_year + selected_month)]
    
#     # Step 5: Extract days from the filtered dates
#     clear_terminal()
#     _, _, days = extract_date_components(filtered_dates)
#     print("Select a day:")
#     selected_day = user_select(days, "Enter the number of the desired day (or press Enter to select the first option): ")
    
#     # Final selected date
#     clear_terminal()
#     selected_date = selected_year + selected_month + selected_day
#     print(f"You have selected the date: {selected_date}")
#     return selected_date

# def detect_outliers(data, high_threshold=2.0, low_threshold=0.5, neighbors=3):
#     """Detect and optionally correct outliers (both high and low) in a dataset."""
#     corrected_data = data.copy()
#     n = len(data)
    
#     for i in range(neighbors, n - neighbors):
#         current_value = data[i]
#         previous_values = data[i-neighbors:i]
#         next_values = data[i+1:i+1+neighbors]
        
#         # Calculate the average of neighboring values
#         neighbor_avg = np.mean(previous_values + next_values)
        
#         # Check if current value is a high outlier
#         if current_value > high_threshold * neighbor_avg:
#             # Ensure surrounding values don't exhibit the same trend
#             surrounding = np.concatenate((previous_values, next_values))
#             if not np.any(surrounding > high_threshold * np.mean(surrounding)):
#                 print(f"High outlier detected at index {i}, value: {current_value}")
#                 corrected_data[i] = neighbor_avg  # Replace with the average of neighbors
        
#         # Check if current value is a low outlier
#         elif current_value < low_threshold * neighbor_avg:
#             # Ensure surrounding values don't exhibit the same trend
#             surrounding = np.concatenate((previous_values, next_values))
#             if not np.any(surrounding < low_threshold * np.mean(surrounding)):
#                 print(f"Low outlier detected at index {i}, value: {current_value}")
#                 corrected_data[i] = neighbor_avg  # Replace with the average of neighbors
                
#     return corrected_data

# # Directory containing the files
# directory = "data_pressure"
# date = main(directory)
# s_path_pressure = f"data_pressure/pressure_{date}.npy"
# data = np.load(s_path_pressure, allow_pickle=True).tolist()
# corrected_data = detect_outliers(data)

# np.save(f"data_pressure/pressure_{date}", corrected_data)


import os
import numpy as np
import re

def clear_terminal():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def list_files(directory):
    """List all .npy files in the directory and extract dates from filenames."""
    files = os.listdir(directory)
    date_pattern = re.compile(r"pressure_(\d{8})\.npy")
    dates = [date_pattern.search(file).group(1) for file in files if date_pattern.search(file)]
    return dates

def extract_date_components(dates):
    """Extract unique years, months, and days from the list of dates."""
    years = sorted(set(date[:4] for date in dates), reverse=True)
    months = sorted(set(date[4:6] for date in dates), reverse=True)
    days = sorted(set(date[6:] for date in dates), reverse=True)
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

def detect_outliers(data, high_threshold=1.7, low_threshold=0.5, neighbors=5):
    """Detect high and low outliers in a dataset."""
    outliers = []
    n = len(data)
    
    for i in range(neighbors, n - neighbors):
        current_value = data[i]
        previous_values = data[i-neighbors:i]
        next_values = data[i+1:i+1+neighbors]
        
        # Calculate the average of neighboring values
        neighbor_avg = np.mean(previous_values + next_values)
        
        # Check if current value is a high outlier
        if current_value > high_threshold * neighbor_avg:
            # Ensure surrounding values don't exhibit the same trend
            surrounding = np.concatenate((previous_values, next_values))
            if not np.any(surrounding > high_threshold * np.mean(surrounding)):
                outliers.append((i, current_value, neighbor_avg))
        
        # Check if current value is a low outlier
        elif current_value < low_threshold * neighbor_avg:
            # Ensure surrounding values don't exhibit the same trend
            surrounding = np.concatenate((previous_values, next_values))
            if not np.any(surrounding < low_threshold * np.mean(surrounding)):
                outliers.append((i, current_value, neighbor_avg))
                
    return outliers

def fix_outliers_interactively(data, outliers):
    """Interactively fix detected outliers."""
    corrected_data = data.copy()
    
    for index, value, neighbor_avg in outliers:
        clear_terminal()
        print(f"Outlier detected at index {index}, value: {value}")
        print(f"Neighboring average: {neighbor_avg}")
        user_input = input("Press Enter to fix this outlier or type 'skip' to leave it: ").strip().lower()
        if user_input != 'skip':
            corrected_data[index] = neighbor_avg
    
    return corrected_data

# Directory containing the files
directory = "data_pressure"
date = main(directory)
s_path_pressure = f"data_pressure/pressure_{date}.npy"
data = np.load(s_path_pressure, allow_pickle=True).tolist()

# Detect outliers
outliers = detect_outliers(data)

if outliers:
    print(f"Detected {len(outliers)} outliers.")
    user_input = input("Press Enter to fix all outliers or type 'select' to choose which ones to fix: ").strip().lower()
    
    if user_input == 'select':
        corrected_data = fix_outliers_interactively(data, outliers)
    else:
        # Automatically fix all outliers
        corrected_data = data.copy()
        for index, value, neighbor_avg in outliers:
            corrected_data[index] = neighbor_avg
else:
    print("No outliers detected.")
    corrected_data = data

# Save the corrected data
np.save(f"data_pressure/pressure_{date}", corrected_data)
print("Corrected data saved.")
