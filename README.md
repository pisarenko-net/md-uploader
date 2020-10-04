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
An example udev rule file is available in this repository.

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

 - python-libusb1 1.8-1
 - python-pycryptodome 3.9.8-2

On arch linux run the following command to install the dependencies:
```
$ sudo pacman -S python-cryptography python-pycryptodome
```

Some libraries are not present in the Arch repositories, such as `translit` and
`tinytag`. Install those separately with pip.

All input tracks are converted into PCM. Hence `ffmpeg` is required to be installed.

## Installing

To build and install the package locally run:

```
$ pip install . 
```

The package installs a script `md_uploader_ctl` into the Python $PATH. With
the help of this script I'm testing individual NetMD API functions.

Once installed, use `md_uploader` package in Python:

```
>>> import md_uploader
>>> net_md = next(md_uploader.devices)  # gives you first available NetMD device
```

An expected interaction looks like the following:
```
playlist_path_name = md_uploader.find_next_playlist_path_name(PLAYLIST_QUEUE_PATH)

playlist = md_uploader.Playlist(PATH_MUSIC, SUPPORTED_EXTENSIONS, playlist_path_name)

net_md = next(devices)

print(playlist.duration())

is_va_disc = not playlist.is_single_artist()
md_disc_title = playlist.title()

net_md.erase_disc()
net_md.set_disc_title(md_disc_title)

for track in playlist:
    md_track_title = track.title if not is_va_disc else '%s - %s' % (track.artist, track.title)

    with md_uploader.TranscodeMD(track.path) as path_pcm:
        (track_number, uuid, ccid) = md_uploader.download_track(net_md, path_pcm, md_track_title)

md_uploader.archive_playlist(playlist_path_name, PLAYLIST_ARCHIVE_PATH)
```

This example is available in the `e2e_test.py` file.
