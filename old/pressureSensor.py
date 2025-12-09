import os
import time
from datetime import datetime
from notion.client import NotionClient
from datetime import datetime
from notion.block import *
from shutil import copyfile
from PIL import Image
i = 0

now = datetime.now()
savestring = now.strftime("%F-%H%M")
directory_new = "/home/bec_lab/Desktop/PressureValues/new/"
directory_cropped = "/home/bec_lab/Desktop/PressureValues/cropped/"
directory_uploaded = "/home/bec_lab/Desktop/PressureValues/uploaded/"

# Take a photo of pressures (first, so that even if there is a problem with notion client, we save a photo)
os.system("fswebcam -r 1920x1080 --jpeg 85 -D 1 --skip 200 /home/bec_lab/Desktop/PressureValues/new/{:}.jpg".format(savestring))

# Initialize the notion client
# try:
client = NotionClient(token_v2="v02%3Auser_token_or_cookies%3A5LyoUimZvV1zCBKj4Lw6k8r4fAMLjG4goVeO2jWLLR-txBSC47r67F5j-SbRoyxLgXzqdGI51b3oV6nWs1CBUAbp-8MtUOy7IBgepGh9Ed1-eeqhqeqZ3TrrCjFkOQ27v_y-")
	# print("Connected.")
# except:
# 	print("Could not connect. Try updating the Token_V2.")
# 	exit()

page = client.get_block("https://www.notion.so/blaznikphd/Pressure-Logbook-613e5aea8cdb4034b05ca31ddf7f39c3")
cv = client.get_collection_view("https://www.notion.so/blaznikphd/05c76530ee9a4f86ad99db6702a7dd5e?v=6aa4421d9e2d497f90f96b73ea8b77ea&pvs=4")




## Check if there are any new photos in the folder - in case it failed previously, we want to upload them all now.
for filename in os.listdir(directory_new):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        i+=1
if i == 0:
    print("There are no new logbook entries.")
else:
    print("Number of new logbook entries:", i)


# Crop the images? Let's try
for filename in os.listdir(directory_new):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        im = Image.open(os.path.join("/home/bec_lab/Desktop/PressureValues/new", filename))
        width, height = im.size
        left = 1 * width/6
        top = 1 * height/8
        right = 3 * width/5
        bottom = height
        im1 = im.crop((left, top, right, bottom))
        im1.save(os.path.join(directory_cropped, filename))
    else:
        continue

if i != 0: print("Crop completed. Now uploading.")

for filename in os.listdir(directory_cropped):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        time.sleep(5)
        row = cv.collection.add_row()
        row.name = filename
        image = row.children.add_new(ImageBlock, width=200)
        image.upload_file(os.path.join(directory_cropped, filename))
        copyfile(os.path.join(directory_cropped, filename), "/storage/pressurelog/" + str(filename))
        os.rename(os.path.join(directory_cropped, filename), os.path.join(directory_uploaded, filename))
    else:
        continue

for filename in os.listdir(directory_new):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        os.remove(os.path.join(directory_new, filename))
    else:
        continue


print("Done")