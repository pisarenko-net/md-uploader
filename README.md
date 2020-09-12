# md-uploader

Headless NetMD Minidisc track uploader. This is a building block towards a Hi-Fi
appliance that I'm putting together.

The purpose of this software is to upload tracks given a playlist. As little interaction
with the user is expected. A typical scenario would be:

 1. user creates a playlist and uploads to a specific folder on NAS
 2. user connects a NetMD with a disc inside to the system
 3. the software detects NetMD
 4. software erases the disc
 5. software converts tracks from FLAC to PCM and uploads to NetMD in SP mode
 6. software sets the disc and track titles according to the playlist

## Important

By default, users won't have sufficient access to the device. The solution is to
update udev rules to grant permission. For testing purposes I'm running this under root.

Sony calls the process of putting tracks onto the devices "downloading". Throughout
the codebase I'm using the term "download". The documentation and the description
instead refer to the term "upload", as in "uploading tracks to the device".

## Attribution

This is made possible by prior work. See linux-minidisc repository at
https://github.com/linux-minidisc/linux-minidisc. Additional refinements were
borrowed from https://github.com/flindroth/netmd.py.

Thank you original authors for reverse engineering the protocol and making
headway into NetMD open-source library code.

The original NetMD python software was updated to work with Python 3. Most code
that is not related to track uploading has been removed. I haven't contributed
Python 3 changes to the original library but the code here can be easily lifted.

## Dependencies

All NetMD-related code has been copied into the project. The software uses the
USB bus to communicate with the device. Nothing else is needed.

python-libusb1 1.8-1
python-pycryptodome 3.9.8-2

On arch linux run the following command to install the dependencies:
```
$ sudo pacman -S python-cryptography python-pycryptodome
```

## Package

To package the software run (or just run without installing but then take care
of the dependencies manually):

```
$ python -m pip install --user --upgrade setuptools wheel
$ python3 setup.py sdist bdist_wheel
```

The package installs a script `md_uploader_ctl` into the Python $PATH. With
the help of this script I'm testing individual NetMD API functions.

