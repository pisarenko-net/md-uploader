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
# net_md.set_disc_title('Fucking fucks')

# with Transcode('/home/sergey/01.wav') as path_pcm:
# 	print("track 1 %s" % path_pcm)
# 	download_track(net_md, path_pcm, "Leafy soil")

# with Transcode('/home/sergey/02.wav') as path_pcm:
# 	print("track 2 %s" % path_pcm)
# 	download_track(net_md, path_pcm, "Exciting rounds")

# with Transcode("/home/sergey/03.wav") as path_pcm:
# 	print("track 3 %s" % path_pcm)
# 	download_track(net_md, path_pcm, "Fanning thins")

# with Transcode("/home/sergey/untitled.wav") as path_pcm:
# 	print("track 4 %s" % path_pcm)
# 	download_track(net_md, path_pcm, "Cuckoo Cock")

# net_md.switch_previous_track()
# net_md.play()
# net_md.set_track_title(0, 'Fucker')
# print(net_md.get_disc_capacity())
