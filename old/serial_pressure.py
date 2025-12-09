import serial.tools.list_ports as port_list
import serial
from time import sleep

ports = list(port_list.comports())
for p in ports:
    print (p)

ser = serial.Serial('/dev/ttyUSB0',19200,bytesize=8,parity='N',stopbits=1,timeout=1)  # open serial port
print(ser.name)         # check which port was really used
print("open: ",ser.is_open)


#for i in range(10):
#    print(i)
ser.write(b'\0x03\0x0d')   # <ETX>
#print(ser.read(10).decode('UTF-8'))

bs=bytearray(b'PR1\0x0d')

for s in range(1,7,1):
    print("--------------------")
    print(f"Pressure Ch. {s}")
    ser.write(b'\0x03\0x0d')   # <ETX>
    bs[2]=s+48
    ser.write(bs)     # write a string
    # sleep(1)
    print(ser.read().decode('UTF-8'))
    sleep(1)
    #for i in range(5):
    ser.write(b'\x05\x0d')     # <ENQ>    print(ser.read().decode('UTF-8'))
    sleep(1)
    print(ser.read(10).decode('UTF-8'),end="")
    sleep(1)
    print("")

ser.close()             # close port
