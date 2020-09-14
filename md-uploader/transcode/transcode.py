import os
import subprocess


__DEV_NULL = open(os.devnull, 'w')


def create_pcm(path):
    filename_out = "/tmp/transcode.out"

    try:
        subprocess.call(['ffmpeg', '-y', '-i', path, '-f', 's16be', filename_out], stdout=__DEV_NULL, stderr=__DEV_NULL)
    except subprocess.CalledProcessError as e:
        filename_out = None

    return filename_out
