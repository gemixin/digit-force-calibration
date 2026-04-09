"""
Collects Grove FSR (A0→GP26) calibration readings on a Raspberry Pi Pico and
appends trial, target weight, time, raw, and voltage values to csv.
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
samples_per_weight = 3   # Number of trials per target weight
capture_duration = 3.0   # Seconds of capture per trial
interval = 0.05          # Sampling interval (~20 Hz)
filename = 'force_calibration.csv'

# Calibration target weights (g) — starting at 25 g due to preload
target_weights = [
    25, 50, 75, 100, 150, 200, 250, 300, 350, 400,
    450, 500, 600, 700, 800, 900, 1000, 1200, 1500
]

# Check if file exists for header
file_exists = filename in os.listdir()

# Open file in append mode once
with open(filename, 'a') as f:
    if not file_exists:
        f.write('trial,target_g,time_s,raw,voltage\n')

    print('\n--- FSR CALIBRATION CAPTURE ---')
    print(f'This will record {samples_per_weight} trials for each target weight.')
    print(f'Each capture lasts {capture_duration} seconds (~{int(capture_duration/interval)} samples).')
    print('Press ENTER when the scale is stable at the target value.\n')

    trial = 1

    # Loop over target weights
    for target in target_weights:
        print(f'\nNext target: {target} g')

        # Repeat readings for each weight
        for rep in range(1, samples_per_weight + 1):

            # Loop until user accepts the trial
            while True:
                input(f'Trial {trial}: Press ENTER to record (target {target} g) → ')
                        
                print(f'Capturing for {capture_duration} seconds...')
                onboard_led.value(1)  # LED on
                
                start = time.ticks_ms()
                trial_data = []  # Temp storage for this trial

                # Capture all samples with timestamps
                while time.ticks_diff(time.ticks_ms(), start) < capture_duration * 1000:
                    elapsed = time.ticks_diff(time.ticks_ms(), start) / 1000  # seconds since start
                    value = fsr.read_u16()  # Read raw ADC (0–65535)
                    voltage = (value / 65535) * VREF  # Convert to voltage
                    trial_data.append(f'{trial},{target},{elapsed:.3f},{value},{voltage:.4f}\n')
                    time.sleep(interval)  # Wait before next sample

                onboard_led.value(0)  # LED off

                # Ask user whether to keep or redo
                choice = input('Keep this trial? (y = keep / r = redo): ').strip().lower()

                if choice == 'y':
                    # Write stored data to file
                    for line in trial_data:
                        f.write(line)
                    f.flush()  # Ensure data is written safely

                    print(f'Trial {trial} complete and appended to {filename}')
                    trial += 1
                    break  # Move to next trial

                elif choice == 'r':
                    print('Redoing trial...')
                    # Do NOT increment trial (overwrite same trial number)
                else:
                    print('Invalid input. Please type y or r.')

print(f'\nAll calibration readings appended to {filename}')
