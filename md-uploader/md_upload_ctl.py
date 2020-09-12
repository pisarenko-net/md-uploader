import os

import usb1

from netmd import netmd_device as devices
from netmd.download import download_track

print("Modify %s to try out different commands. By default this does nothing." % os.path.realpath(__file__))

try:
    netmd = next(devices)  # grabs first connected NetMD, or throws StopIteration exception if there are none
except StopIteration:
    print("No NetMD devices found.")
    exit(1)
except usb1.USBErrorAccess:
    print("Your user doesn't have sufficient access. Either try with root or better setup a udev rule.")
    exit(1)

# Uncomment one or more to execute the command

# netmd.erase_disc()
# download_track(netmd, "test.wav", "Take it eeeeaaaaasyyyyy")
