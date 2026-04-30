"""
Collects Grove FSR (A0→GP26) readings on a Raspberry Pi Pico and
appends object/motion/force labels with raw and voltage values to csv.
"""

from machine import ADC, Pin
import time
import os

# Setup the sensor
fsr = ADC(Pin(26))  # Grove A0 → GP26 (ADC0)
VREF = 3.3  # Grove Shield set to 3.3v

# Setup the onboard LED
onboard_led = Pin(25, Pin.OUT)

# Settings
duration = 5.0  # Seconds of capture
interval = 0.1  # Sampling interval (~10 Hz)
prep_time = 3  # Countdown seconds before capture starts
filename = "motion_data.csv"

# Get object label from user
object_label = input("Enter object label: ")

# Motions and force levels
motions = ["slide", "rotate"]
force_levels = [1, 2, 3]

# Check if file exists for header
file_exists = filename in os.listdir()

# Open file in append mode once
with open(filename, "a") as f:
    if not file_exists:
        f.write("object,motion,force,raw,voltage\n")

    # Loop over force levels and motions
    for force in force_levels:
        for motion in motions:
            print(f"\nNext capture: {motion} with force level {force}")
            print("Press ENTER to start capture...")
            input()

            # Countdown before capture
            print("Get ready!")
            for i in range(prep_time, 0, -1):
                print(f"{i}...")
                time.sleep(1)

            print(f"Capturing for {duration} seconds...")
            onboard_led.value(1)  # LED on

            start = time.ticks_ms()
            data = []

            # Capture loop
            while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
                value = fsr.read_u16()  # Read raw ADC (0–65535)
                voltage = (value / 65535) * VREF  # Convert to voltage
                data.append(f"{object_label},{motion},{force},{value},{voltage:.4f}")
                time.sleep(interval)  # Wait before next sample

            # Write captured data to file
            f.write("\n".join(data) + "\n")

            onboard_led.value(0)  # LED off
            print(f"Data appended to {filename}")
            print("Capture complete.")

print("\nAll captures complete.")
