import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# 1. Initialize the I2C interface
i2c = busio.I2C(board.SCL, board.SDA)

# 2. Create the ADS object
ads = ADS.ADS1115(i2c)

# 3. Create an analog input channel on Pin 0 (A0)
chan = AnalogIn(ads, ADS.P0)

print("Reading ADS1115 on A0. Press Ctrl+C to stop.")
print("-" * 40)

try:
    while True:
        # Read the raw value (0-32767) and the calculated voltage
        raw_value = chan.value
        voltage = chan.voltage
        
        # Print to console, formatting to 3 decimal places
        print(f"Raw Value: {raw_value:>6}  |  Voltage: {voltage:>5.3f} V")
        
        # Pause for half a second before the next read
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nProgram stopped by user.")
