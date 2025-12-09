import pytesseract
from matplotlib import pyplot as plt
from datetime import datetime
import time 
from PIL import Image
import matplotlib.dates as mdates
from os import listdir
from os.path import isfile, join
import numpy as np


# THIS PART IS IF YOU NEED TO EXTRACT THE PRESSURES FROM THE IMAGES
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
# Initialize a list to store time and pressure data
times = []
pressures = []
mypath = "/home/bec_lab/python/PRESSURE/images_pressure/"
onlyfiles = [join(mypath, f) for f in sorted(listdir(mypath)) if isfile(join(mypath, f))]
i = 0

def clean_extracted_text(extracted_text):
    # Define the allowed characters
    allowed_chars = set("0123456789.E-")
    # Filter out any characters not in the allowed_chars
    cleaned_text = ''.join([char for char in extracted_text if char in allowed_chars])
    return cleaned_text

for file in onlyfiles:
    im = Image.open(file)    
    im = np.array(im)[:, 235:490]
    text = pytesseract.image_to_string(im, config='--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.E-')
    text = clean_extracted_text(text)

    try:
        if len(text) > 5 and text[-4] == 'E':
            dtime = file[-19:-4]
            stime = datetime.strptime(dtime, "%Y%m%d_%H%M%S")
            if text[1] == '.':
                pressure = float(text[:8])
            else:                
                pressure = float(text[:1] + "." + text[1:8])
            print(f"{i}/{len(onlyfiles)} --- {stime} - {pressure}")
            times.append(stime)
            pressures.append(pressure)
        else: 
            continue
    except:
        print(f"{i}/{len(onlyfiles)} --- {stime} - N/A")
        continue
    
    i += 1

np.save("data_pressure/times", times)
np.save("data_pressure/pressure", pressures)

#quit()

np.load("data_pressure/times.npy", allow_pickle=True).aslist()
np.load("data_pressure/pressure.npy", allow_pickle=True).aslist()

fig, ax = plt.subplots()
plt.plot(times, pressures, 'r-', alpha=0.75)
plt.gcf().autofmt_xdate()  # Auto-format date on the x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Set x-axis format to HH:MM
ax.set_xlabel('Time (HH:MM)')
ax.set_ylabel('Pressure (mbar)')
ax.set_title('Real-time Pressure Monitoring')
plt.show() 

