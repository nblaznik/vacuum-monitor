from tpg_256a_pressure_monitor import Monitor
# Establish connection
gauge = Monitor(port='/dev/ttyUSB0')  # Use the correct port for your setup

try:
    # Read and print pressure
    pressure = gauge.read_pressure()
    print(f"Current pressure: {pressure} mbar")
except Exception as e:
    print(f"Failed to read pressure: {e}")
finally:
    # Close the connection
    gauge.close()
