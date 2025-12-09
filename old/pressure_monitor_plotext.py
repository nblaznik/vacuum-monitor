"""     This code is only meant for live previewing of the pressures in the setup, with the plots being output straight in the terminal. For displaying older dates, see a different code. """

import cv2
import pytesseract
from datetime import datetime
import time
from PIL import Image
import plotext as plt
import numpy as np 
import matplotlib.pyplot as mplt
import matplotlib.dates as mdates
import os 
from scipy.signal import savgol_filter
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Date specific saving
old_date = datetime.now().strftime('%Y%m%d')
s_path_time = f"data_pressure/times_{old_date}.npy"
s_path_pressure = f"data_pressure/pressure_{old_date}.npy"

if os.path.exists(s_path_time) and os.path.exists(s_path_pressure):
    print("Dates exist - loading.")
    times = np.load(s_path_time, allow_pickle=True).tolist()
    pressures = np.load(s_path_pressure, allow_pickle=True).tolist()

else: 
    print("New date, creating new files.")
    times = []
    pressures = []

# This I think is if the code is (somehow) interrupted just between the savings. 
if len(times) > len(pressures):
    times = times[:len(pressures)]

elif len(times) < len(pressures):
    pressures = pressures[:len(times)]

np.save(f"data_pressure/times_{old_date}", times)
np.save(f"data_pressure/pressure_{old_date}", pressures)


def clean_extracted_text(extracted_text):
    # Define the allowed characters
    allowed_chars = set("0123456789.E-")
    # Filter out any characters not in the allowed_chars
    cleaned_text = ''.join([char for char in extracted_text if char in allowed_chars])
    return cleaned_text


def plot_data(times, pressures):
    # Clear the terminal
    plt.clf()

    if not pressures:
        print("No data to plot.")
        return

    # Convert time to a format that can be plotted
    plt.date_form('H:M:S')
    x = plt.datetimes_to_string(times)
    y = [p / 1e-6 for p in pressures] # fix the y scale. 

    # Plot line graph
    label = f"Last {pressures[-1]} mbar at {times[-1]}"
    plt.plot(x, y, label=label, color="black", marker='braille')
    plt.scatter(x, savgol_filter(y, window_length=max(3, len(y)//10), polyorder=2), color='red+', marker='braille')
    plt.xlabel("Time (HH:MM)")
    plt.ylabel("Pressure (1e-6 x mbar)")
    plt.title("Pressures CH. 4")

    plt.show()

try: 
    while True:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        #print(ret, frame)
        #cv2.imwrite("images_pressure/pressure.png", frame[200:300, 225:500])
        #im = Image.open("images_pressure/pressure.png")
        #print(pytesseract.image_to_string(im, config="--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.E-"))
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            text_img = gray[200:300, 235:490]
            dtime = datetime.now().strftime('%Y%m%d_%H%M%S')
            date =  datetime.now().strftime('%Y%m%d')
            if date != old_date:
                # then save old files 
                np.save(f"data_pressure/times_{old_date}", times)
                np.save(f"data_pressure/pressure_{old_date}", pressures)
                times = []          # reset the array 
                pressures = []      # reset the array
                old_date = date     # modify the old date. 

            else: 
                times = np.load(f"data_pressure/times_{date}.npy", allow_pickle=True).tolist()
                pressures = np.load(f"data_pressure/pressure_{date}.npy", allow_pickle=True).tolist()
                # Load them each time, so that any updates to the files (fixing outliers) are immediately in effect 

            # Save image, read it, then delete it
            filename = f"images_pressure/pressure_reading_{dtime}.png"
            cv2.imwrite(filename, text_img)
            im = Image.open(filename)
            text = pytesseract.image_to_string(im, config='--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.E-')
            text = clean_extracted_text(text)
            os.remove(filename)
            try: 
                if len(text) > 5:
                    stime = datetime.strptime(dtime, "%Y%m%d_%H%M%S")
                    
                    if text[1] == '.':
                        pressure = float(text[:8])
                    else:
                        pressure = float(text[:1] + "." + text[1:8])
                        
                    times.append(stime)
                    pressures.append(pressure)
                    
                    # Save the arrays - otherwise an error here will mess everything up. Trust me. 
                    np.save(f"data_pressure/times_{date}", times)
                    np.save(f"data_pressure/pressure_{date}", pressures)

                    # Plot the data to the terminal
                    plot_data(times, pressures)
            except Exception as error:
                # handle the exception
                print("An exception occurred:", error)                 
            time.sleep(2)  # Wait for 2 seconds before capturing the next image
                    

except KeyboardInterrupt: 
    # Save, and display the final plot.             
    date =  datetime.now().strftime('%Y%m%d')

    # This I think is if the code is (somehow) interrupted just between the savings. 
    if len(times) > len(pressures):
        times = times[:len(pressures)]

    elif len(times) < len(pressures):
        pressures = pressures[:len(times)]

    np.save(f"data_pressure/times_{date}", times)
    np.save(f"data_pressure/pressure_{date}", pressures)
    print("Files successfuly saved")

    fig, ax = mplt.subplots()
    mplt.plot(times, pressures, 'r-', alpha=0.12)
    mplt.scatter(times, pressures, c='r', alpha=0.75)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    mplt.gcf().autofmt_xdate()  # Auto-format date on the x-axis
    mplt.xlabel("Time (HH:MM)")
    ax.set_xlabel('Time')
    ax.set_ylabel('Pressure (mbar)')
    ax.set_title(f"Pressure CH.4") # on {times[-1].strftime('%Y-%m-%d')}")

    mplt.show() 
