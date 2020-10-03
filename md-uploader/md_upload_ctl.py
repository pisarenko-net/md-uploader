import os

import usb1

from netmd import netmd_device as devices
from netmd.download import download_track
from transcode import Transcode


print("Modify %s to try out different commands. By default this does nothing." % os.path.realpath(__file__))

try:
    net_md = next(devices)  # grabs first connected NetMD, or throws StopIteration exception if there are none
except StopIteration:
    print("No NetMD devices found.")
    exit(1)
except usb1.USBErrorAccess:
    print("Your user doesn't have sufficient access. Either try with root or better setup a udev rule.")
    exit(1)

# Uncomment one or more to execute the command

# net_md.erase_disc()
#print(net_md.get_disc_title())
#net_md.set_disc_title('Testing commands')

# with Transcode("/home/sergey/03.wav") as path_pcm:
# 	print("track 1 %s" % path_pcm)
# 	download_track(net_md, path_pcm, "Take it eeeeaaaaasyyyyy")

# with Transcode("/home/sergey/untitled.wav") as path_pcm:
# 	print("track 2 %s" % path_pcm)
# 	download_track(net_md, path_pcm, "More than you know")

# with Transcode("/home/sergey/02.wav") as path_pcm:
# 	print("track 3 %s" % path_pcm)
# 	download_track(net_md, path_pcm, "Flying past the eye")

