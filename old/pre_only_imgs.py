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




try: 
    while True:
        dtime = datetime.now().strftime('%Y%m%d_%H%M%S')
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        filename = f"images_pressure/pressure_reading_{dtime}.png"
        cv2.imwrite(filename, frame[200:300])
        cap.release()
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
