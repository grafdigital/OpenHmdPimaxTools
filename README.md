# Helper Scripts for Pimax 4K with OpenHMD

This collection of scripts was used to get the Pimax 4k working with OpenHMD.
Most of the code here was taken from random generic code examples for Gyroscope & Accelerometer Arduino breakout boards, adapted to python and mangled to get it to work with the reverse engineered HID data from the Pimax.
Depending on your system you may need to run these scripts as root.

## Gyro Calibration
> pimax_gyro_calibration.py

If your HMD drifts with our magic values, you may need to calibrate your gyro. For this, set the Pimax down onto a level and still surface in normal orientation. Run the script and don't touch the HMD, it will collect 1000 samples, calculate the gyro offset and print it to the console. Take the result and replace the magic number line in pimax.c with your values.

## Set Pimax HMD Resolution
> pimax_hmd_set_resolution.py [read,high,low]

The Pimax 4k has two resolution modes. With this tool you can read or set the resolution without using PiTool. The high mode gives you a more crisp image at the cost of refresh rate (60Hz vs 90hz).

## Magnetometer
> pimax_mag_debug.py
> pimax_mag_calibration.py

These are experimental and unfinished scripts to make sense of the magnetometer data.

## Disclaimer
We are not affiliated with Pimax Inc. This is only an attempt at bringing compatibility for the Pimax 4K to Linux. Use these scripts at your own risk. We are not responsible for bricked headsets.
