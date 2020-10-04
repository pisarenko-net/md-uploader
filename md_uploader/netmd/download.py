import array
import math
import os
import random

from Crypto.Cipher import DES
from Crypto.Cipher import DES3

from .constants import KEK
from .constants import ROOT_KEY
from .constants import WIREFORMAT_LP2
from .constants import WIREFORMAT_PCM
from .constants import WIRE_TO_DISK_FORMAT
from .constants import WIRE_TO_FRAME_SIZE
from .exception import NetMDNotImplemented
from .util import bytes_to_str
from .util import create_iv


def download_track(net_md, wav_filename, title):
    try:
        net_md.disable_new_track_protection(1)
    except NetMDNotImplemented:
        print("Can't set device to non-protecting")

    with MDSession(net_md) as session:
        track = MDTrack(wav_filename, title, WIREFORMAT_PCM)
        return session.download_track(track)


class MDTrack(object):
    __PACKET_SIZE = 2048

    def __init__(self, filename, title, wireformat):
        self.filename = filename
        self.title = title
        self.wireformat = wireformat
        self.framesize = WIRE_TO_FRAME_SIZE[wireformat]

    def get_frame_count(self):
        filesize = os.path.getsize(self.filename)
        framecount = filesize // self.framesize
        
        misalignment = filesize % 8
        if misalignment != 0:
            framecount = framecount - 1
        
        return framecount

    def get_packet_count(self):
        numpackets = int(math.ceil(float(self.get_frame_count()) / MDTrack.__PACKET_SIZE))
        return numpackets

    def get_packets(self):
        # values do not matter at all
        datakey = b"\x96\x03\xc7\xc0\x53\x37\xd2\xf0"
        firstiv = b"\x08\xd9\xcb\xd4\xc1\x5e\xc0\xff"
        keycrypter = DES.new(KEK, DES.MODE_ECB)
        key = keycrypter.encrypt(datakey)
        datacrypter = DES.new(key, DES.MODE_CBC, firstiv)

        with open(self.filename, 'rb') as file:
            packets = []
            data = None

            framesremaining = self.get_frame_count()
            for i in range(0, self.get_packet_count()):
                if framesremaining < MDTrack.__PACKET_SIZE:
                    data = file.read(framesremaining * self.framesize)
                else:
                    data = file.read(MDTrack.__PACKET_SIZE * self.framesize)
                    framesremaining = framesremaining - MDTrack.__PACKET_SIZE
                packets.append((datakey, firstiv, datacrypter.encrypt(data)))

        return packets


class MDSession(object):
    def __init__(self, net_md):
        self.net_md = net_md

    def __enter__(self):
        try:
            self.net_md.forget_session_key()
            self.net_md.leave_secure_session()
        except:
            None

        self.net_md.enter_secure_session()
        self.net_md.send_key_data()

        hostnonce = bytes_to_str([random.randrange(255) for x in range(8)])
        devnonce = self.net_md.exchange_session_key(hostnonce)
        nonce = hostnonce + devnonce
        self.sessionkey = self._get_retail_mac(ROOT_KEY, nonce)

        return self

    def __exit__(self, type, value, traceback):
        if self.sessionkey != None:
            self.net_md.forget_session_key()
            self.sessionkey = None
        self.net_md.leave_secure_session()

    def download_track(self, track):
        self.net_md.setup_download(self.sessionkey)
        wireformat = track.wireformat
        
        (track_number, uuid, ccid) = self.net_md.send_track(
            wireformat,
            WIRE_TO_DISK_FORMAT[wireformat],
            track.get_frame_count(),
            track.get_packet_count(),
            track.get_packets(),
            self.sessionkey
        )
        
        self.net_md.cache_toc()
        self.net_md.set_track_title(track_number, track.title)
        self.net_md.sync_toc()
        self.net_md.commit_track(track_number, self.sessionkey)

        return (track_number, bytes_to_str(uuid), bytes_to_str(ccid))

    def _get_retail_mac(self, key, value):
        byte_value = bytearray([ord(c) for c in value])
        subkeyA = key[0:8]
        beginning = byte_value[0:-8]
        end = byte_value[-8:]

        iv = create_iv()
        step1crypt = DES.new(subkeyA, DES.MODE_CBC, iv)

        iv2 = step1crypt.encrypt(beginning)[-8:]
        step2crypt = DES3.new(key, DES3.MODE_CBC, iv2)

        return step2crypt.encrypt(end)
