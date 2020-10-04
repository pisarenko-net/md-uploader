import os
import subprocess
import tempfile


DEV_NULL = open(os.devnull, 'w')


class Transcode(object):
    def __init__(self, track_filename):
        self.track_filename = track_filename
        (_, filename_out) = tempfile.mkstemp()
        self.transcoded_filename = filename_out

    def __enter__(self):
        try:
            subprocess.call(['ffmpeg', '-y', '-i', self.track_filename, '-f', 's16be', self.transcoded_filename], stdout=DEV_NULL, stderr=DEV_NULL)
        except subprocess.CalledProcessError as e:
            filename_out = None

        return self.transcoded_filename

    def __exit__(self, type, value, traceback):
        os.remove(self.transcoded_filename)
