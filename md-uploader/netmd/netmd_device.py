"""NetMD interface

High-level interface to NetMD devices.

The module itself is iterable. Getting all supported devices is as simple as:
```
import netmd_device as devices

for netmd in devices:
    # do something with the device, e.g. pass to higher level interface

```
"""

import sys
from struct import pack

from Crypto.Cipher import DES
from Crypto.Cipher import DES3

from .constants import KEK
from .constants import WIRE_TO_FRAME_SIZE
from .exception import NetMDException
from .exception import NetMDNotImplemented
from .exception import NetMDRejected
from . import usb_device as devices
from .util import bytes_to_str
from .util import create_iv
from .util import str_to_bytearray


class NetMDDevicesModule(object):
    def __init__(self):
        pass

    def __iter__(self):
      """
        Iterator for plugged-in NetMD devices.

        Returns (yields) NetMD instances.
      """
      for dev in devices:
          yield NetMD(dev)


class NetMD(object):
    """
      High-level interface for a NetMD device.
      Notes:
        Track numbering starts at 0.
        First song position is 0:0:0'1 (0 hours, 0 minutes, 0 second, 1 sample)
        wchar titles are probably shift-jis encoded (hint only, nothing relies
          on this in this file)
    """

    # NetMD Protocol return status (first byte of request)
    __STATUS_CONTROL = 0x00
    __STATUS_STATUS = 0x01
    __STATUS_SPECIFIC_INQUIRY = 0x02
    __STATUS_NOTIFY = 0x03
    __STATUS_GENERAL_INQUIRY = 0x04
    # ... (first byte of response)
    __STATUS_IN_TRANSITION = 0x0b
    __STATUS_NOT_IMPLEMENTED = 0x08
    __STATUS_IMPLEMENTED = 0x0c
    __STATUS_CHANGED = 0x0d
    __STATUS_INTERIM = 0x0f
    __STATUS_ACCEPTED = 0x09
    __STATUS_REJECTED = 0x0a

    __FORMAT_TYPE_LEN_DICT = {
        'b': 1, # byte
        'w': 2, # word
        'd': 4, # doubleword
        'q': 8, # quadword
    }

    __ACTION_PLAY = 0x75
    __ACTION_PAUSE = 0x7d
    __ACTION_FASTFORWARD = 0x39
    __ACTION_REWIND = 0x49

    __TRACK_PREVIOUS = 0x0002
    __TRACK_NEXT = 0x8001
    __TRACK_RESTART = 0x0001

    __DISC_FLAG_WRITABLE = 0x10
    __DISC_FLAG_WRITE_PROTECTED = 0x40

    __CONTENT_ID = b"\x01\x0F\x50\0\0\4\0\0\0" + b"\x48\xA2\x8D\x3E\x1A\x3B\x0C\x44\xAF\x2f\xa0"
    __EKBID = 0x26422642 #"\x06\xec\xfa\xb1\xc8\xa2\x1b\xfd"
    __EKB_DATA = (
        [
            "\x25\x45\x06\x4d\xea\xca\x14\xf9\x96\xbd\xc8\xa4\x06\xc2\x2b\x81",
            "\xfb\x60\xbd\xdd\x0d\xbc\xab\x84\x8a\x00\x5e\x03\x19\x4d\x3e\xda"
        ],
        9,
        "\x8f\x2b\xc3\x52\xe8\x6c\x5e\xd3\x06\xdc\xae\x18\xd2\xf3\x8c\x7f\x89\xb5\xe1\x85\x55\xa1\x05\xea"
    )

    def __init__(self, net_md_usb):
        """
          net_md (NetMD)
            Interface to the NetMD device to use.
        """
        self.net_md_usb = net_md_usb

    #
    # Disc wide controls
    #

    def erase_disc(self):
        """
          Erase disc.
          This is reported not to check for any track protection, and
          unconditionaly erases everything.
        """
        # XXX: test to see if it honors read-only disc mode.
        reply = self.__send_query('1840 ff 0000')
        self.__parse_response(reply, '1840 00 0000')

    def sync_toc(self):
        reply = self.__send_query('1808 10180200 00')
        return self.__parse_response(reply, '1808 10180200 00')

    def cache_toc(self):
        reply = self.__send_query('1808 10180203 00')
        return self.__parse_response(reply, '1808 10180203 00')

    #
    # Playback controls
    #

    def play(self):
        """
          Start playback on device.
        """
        self._play(NetMD.__ACTION_PLAY)

    def _play(self, action):
        reply = self.__send_query('18c3 ff %b 000000', action)
        self.__parse_response(reply, '18c3 00 %b 000000')

    def pause(self):
        """
          Pause device.
        """
        self._play(NetMD.__ACTION_PAUSE)

    def fast_forward(self):
        """
          Fast-forward device.
        """
        self._play(NetMD.__ACTION_FASTFORWARD)

    def rewind(self):
        """
          Rewind device.
        """
        self._play(NetMD.__ACTION_REWIND)

    def stop(self):
        """
          Stop playback on device.
        """
        reply = self.__send_query('18c5 ff 00000000')
        self.__parse_response(reply, '18c5 00 00000000')

    def switch_next_track(self):
        """
          Go to begining of next track.
        """
        self.__change_track(NetMD.__TRACK_NEXT)

    def __change_track(self, direction):
        reply = self.__send_query('1850 ff10 00000000 %w', direction)
        return self.__parse_response(reply, '1850 0010 00000000 %?%?')

    def switch_previous_track(self):
        """
          Go to begining of previous track.
        """
        self.__change_track(NetMD.__TRACK_PREVIOUS)

    def restart_track(self):
        """
          Go to begining of current track.
        """
        self.__change_track(NetMD.__TRACK_RESTART)

    def go_to_track(self, track):
        """
          Seek to begining of given track number on device.
        """
        reply = self.__send_query('1850 ff010000 0000 %w', track)
        return self.__parse_response(reply, '1850 00010000 0000 %w')[0]

    def go_to_time(self, track, hour=0, minute=0, second=0, frame=0):
        """
          Seek to given time of given track.
        """
        reply = self.__send_query('1850 ff000000 0000 %w %b%b%b%b', track,
                                  int2BCD(hour), int2BCD(minute),
                                  int2BCD(second), int2BCD(frame))
        return self.__parse_response(reply, '1850 00000000 %?%? %w %b%b%b%b')

    #
    # Titling
    #

    def get_disc_title(self, wchar=False):
        """
          Return disc title.
          wchar (bool)
            If True, return the content of wchar title.
            If False, return the ASCII title.
        """
        title = self._get_disc_title(wchar=wchar)
        if title.endswith('//'):
            # this is a grouped minidisc which may have a disc title
            # The disc title is always stored in the first entry and
            # applied to the imaginary track 0
            firstentry = title.split('//')[0]
            if firstentry.startswith('0;'):
                title = firstentry[2:len(firstentry)];
            else:
                title = '';
        return title

    def _get_disc_title(self, wchar=False):
        # XXX: long title support untested.
        if wchar:
            wchar_value = 1
        else:
            wchar_value = 0
        done = 0
        remaining = 0
        total = 1
        result = []
        while done < total:
            reply = self.__send_query('1806 02201801 00%b 3000 0a00 ff00 %w%w',
                                      wchar_value, remaining, done)
            if remaining == 0:
                chunk_size, total, chunk = self.__parse_response(reply,
                    '1806 02201801 00%? 3000 0a00 1000 %w0000 %?%?000a %w %*')
                chunk_size -= 6
            else:
                chunk_size, chunk = self.__parse_response(reply,
                    '1806 02201801 00%? 3000 0a00 1000 %w%?%? %*')
            assert chunk_size == len(chunk)
            result.append(chunk)
            done += chunk_size
            remaining = total - done
        #if not wchar and len(result):
        #    assert result[-1] == '\x00'
        #    result = result[:-1]
        return ''.join(result)

    def set_disc_title(self, title, wchar=False):
        """
          Set disc title.
          title (str)
            The new title.
          wchar (bool)
            If True, return the content of wchar title.
            If False, return the ASCII title.
        """
        if wchar:
            wchar = 1
        else:
            wchar = 0
        old_len = len(self._get_disc_title())
        reply = self.__send_query('1807 02201801 00%b 3000 0a00 5000 %w 0000 ' \
                                  '%w %s', wchar, len(title), old_len, title)
        self.__parse_response(reply, '1807 02201801 00%? 3000 0a00 5000 %?%? 0000 ' \
                              '%?%?')

    def get_track_title(self, track, wchar=False):
        """
          Return track title.
          track (int)
            Track number.
          wchar (bool)
            If True, return the content of wchar title.
            If False, return the ASCII title.
        """
        if wchar:
            wchar_value = 3
        else:
            wchar_value = 2
        reply = self.__send_query('1806 022018%b %w 3000 0a00 ff00 00000000',
                                  wchar_value, track)
        result = self.__parse_response(reply, '1806 022018%? %?%? %?%? %?%? 1000 ' \
                                '00%?0000 00%?000a %x')[0]
        #if not wchar and len(result):
        #    assert result[-1] == '\x00'
        #    result = result[:-1]
        return result

    def set_track_title(self, track, title, wchar=False):
        """
          Set track title.
          track (int)
            Track to retitle.
          title (str)
            The new title.
          wchar (bool)
            If True, return the content of wchar title.
            If False, return the ASCII title.
        """
        if wchar:
            wchar = 3
        else:
            wchar = 2
        try:
            old_len = len(self.get_track_title(track))
        except NetMDRejected:
            old_len = 0
        reply = self.__send_query('1807 022018%b %w 3000 0a00 5000 %w 0000 ' \
                                  '%w %*', wchar, track, len(title), old_len,
                                  title)
        self.__parse_response(reply, '1807 022018%? %?%? 3000 0a00 5000 %?%? 0000 ' \
                              '%?%?')

    #
    # Disc status
    #

    def is_disk_present(self):
        """
          Is a disk present in device ?
          Returns a boolean:
            True: disk present
            False: no disk
        """
        status = self.__get_status()
        return status[4] == 0x40

    def __get_status(self):
        """
          Get device status.
          Returns device response (content meaning is largely unknown).
        """
        reply = self.__send_query('1809 8001 0230 8800 0030 8804 00 ff00 ' \
                                  '00000000')
        return self.__parse_response(reply, '1809 8001 0230 8800 0030 8804 00 ' \
                              '1000 000900000 %x')[0]

    def get_disc_capacity(self):
        """
          Get disc capacity.
          Returns a list of 3 lists of 4 elements each (see getTrackLength).
          The first list is the recorded duration.
          The second list is the total disc duration (*).
          The third list is the available disc duration (*).
          (*): This result depends on current recording parameters.
        """
        reply = self.__send_query('1806 02101000 3080 0300 ff00 00000000')
        raw_result = self.__parse_response(reply, '1806 02101000 3080 0300 1000 ' \
                                    '001d0000 001b 8003 0017 8000 0005 %w ' \
                                    '%b %b %b 0005 %w %b %b %b 0005 %w %b ' \
                                    '%b %b')
        result = []
        for offset in range(3):
            offset *= 4
            result.append([
                BCD2int(raw_result[offset + 0]),
                BCD2int(raw_result[offset + 1]),
                BCD2int(raw_result[offset + 2]),
                BCD2int(raw_result[offset + 3])])
        return result

    def is_disk_writeable(self):
        """
          UNTESTED
        """
        status = self.__get_disc_flags()
        return status[4] == NetMD.__DISC_FLAG_WRITABLE

    def __get_disc_flags(self):
        """
          Get disc flags.
          Returns a bitfield (see DISC_FLAG_* constants).
        """
        reply = self.__send_query('1806 01101000 ff00 0001000b')
        return self.__parse_response(reply, '1806 01101000 1000 0001000b %b')[0]

    def is_disk_write_protected(self):
        """
          UNTESTED
        """
        status = self.__get_disc_flags()
        return status[4] == NetMD.__DISC_FLAG_WRITE_PROTECTED

    #
    # Track status
    #

    def get_track_count(self):
        """
          Get the number of disc tracks.
        """
        reply = self.__send_query('1806 02101001 3000 1000 ff00 00000000')
        data = self.__parse_response(reply, '1806 02101001 %?%? %?%? 1000 00%?0000 ' \
                              '%x')[0]
        assert len(data) == 6, len(data)
        assert data[:5] == '\x00\x10\x00\x02\x00', data[:5]
        return ord(data[5])

    def get_track_length(self, track):
        """
          Get track duration.
          track (int)
            Track to fetch information from.
          Returns a list of 4 elements:
          - hours
          - minutes
          - seconds
          - samples (512 per second)
        """
        raw_value = self._get_track_info(track, 0x3000, 0x0100)
        result = self.__parse_response(raw_value, '0001 0006 0000 %b %b %b %b')
        result[0] = BCD2int(result[0])
        result[1] = BCD2int(result[1])
        result[2] = BCD2int(result[2])
        result[3] = BCD2int(result[3])
        return result

    def _get_track_info(self, track, p1, p2):
        reply = self.__send_query('1806 02201001 %w %w %w ff00 00000000', track,
                                  p1, p2)
        return self.__parse_response(reply, '1806 02201001 %?%? %?%? %?%? 1000 ' \
                              '00%?0000 %x')[0]

    def get_track_position(self):
        try:
            reply = self.__send_query('1809 8001 0430 8802 0030 8805 0030 0003 ' \
                                      '0030 0002 00 ff00 00000000')
        except NetMDRejected: # No disc
            result = None
        else:
            result = self.__parse_response(reply, '1809 8001 0430 %?%? %?%? %?%? ' \
                                    '%?%? %?%? %?%? %?%? %? %?00 00%?0000 ' \
                                    '000b 0002 0007 00 %w %b %b %b %b')
            result[1] = BCD2int(result[1])
            result[2] = BCD2int(result[2])
            result[3] = BCD2int(result[3])
            result[4] = BCD2int(result[4])
        return result

    def get_track_uuid(self, track):
        """
         Gets the DRM tracking ID for a track.
         NetMD downloaded tracks have an 8-byte identifier (instead of their
         content ID) stored on the MD medium. This is used to verify the
         identity of a track when checking in.
         track (int)
           The track number
         Returns
           An 8-byte binary string containing the track UUID.
        """
        reply = self.__send_query('1800 080046 f0030103 23 ff 1001 %w', track)
        return self.__parse_response(reply,'1800 080046 f0030103 23 00 1001 %?%? %*')[0]

    #
    # Track editing
    #

    def erase_track(self, track):
        """
          Remove a track.
          track (int)
            Track to remove.
        """
        reply = self.__send_query('1840 ff01 00 201001 %w', track)
        self.__parse_response(reply, '1840 1001 00 201001 %?%?')

    def move_track(self, source, dest):
        """
          Move a track.
          source (int)
            Track position before moving.
          dest (int)
            Track position after moving.
        """
        reply = self.__send_query('1843 ff00 00 201001 00 %w 201001 %w', source,
                                  dest)
        self.__parse_response(reply, '1843 0000 00 201001 00 %?%? 201001 %?%?')

    #
    # Sessions
    #

    def enter_secure_session(self):
        """
         Enter a session secured by a root key found in an EKB. The
         EKB for this session has to be download after entering the
         session.
        """
        reply = self.__send_query('1800 080046 f0030103 80 ff')
        return self.__parse_response(reply, '1800 080046 f0030103 80 00')

    def leave_secure_session(self):
        """
         Forget the key material from the EKB used in the secure
         session.
        """
        reply = self.__send_query('1800 080046 f0030103 81 ff')
        return self.__parse_response(reply, '1800 080046 f0030103 81 00')

    def get_leaf_id(self):
        """
         Read the leaf ID of the present NetMD device. The leaf ID tells
         which keys the device posesses, which is needed to find out which
         parts of the EKB needs to be sent to the device for it to decrypt
         the root key.
         The leaf ID is a 8-byte constant
        """
        reply = self.__send_query('1800 080046 f0030103 11 ff')
        return self.__parse_response(reply, '1800 080046 f0030103 11 00 %*')[0]

    def send_key_data(self):
        """
         Send key data to the device. The device uses it's builtin key
         to decrypt the root key from an EKB.
         ekbid (int)
           The ID of the EKB.
         keychain (list of 16-byte str)
           A chain of encrypted keys. The one end of the chain is the
           encrypted root key, the other end is a key encrypted by a key
           the device has in it's key set. The direction of the chain is
           not yet known.
         depth (str)
           Selects which key from the devices keyset has to be used to
           start decrypting the chain. Each key in the key set corresponds
           to a specific depth in the tree of device IDs.
         ekbsignature
           A 24 byte signature of the root key. Used to verify integrity
           of the decrypted root key by the device.
        """
        keychain, depth, ekbsignature = NetMD.__EKB_DATA

        chainlen = len(keychain)
        # 16 bytes header, 16 bytes per key, 24 bytes for the signature
        databytes = 16 + 16*chainlen + 24
        for key in keychain:
            if len(key) != 16:
                raise ValueError("Each key in the chain needs to have 16 bytes, this one has %d" % len(key))
        if depth < 1 or depth > 63:
            raise ValueError('Supplied depth is invalid')
        if len(ekbsignature) != 24:
            raise ValueError('Supplied EKB signature length wrong')
        reply = self.__send_query('1800 080046 f0030103 12 ff %w %d' \
                                  '%d %d %d 00000000 %* %*', databytes, databytes,
                                  chainlen, depth, NetMD.__EKBID, "".join(keychain), ekbsignature)
        return self.__parse_response(reply, '1800 080046 f0030103 12 01 %?%? %?%?%?%?')

    def exchange_session_key(self, hostnonce):
        """
         Exchange a session key with the device. Needs to have a root
         key sent to the device using sendKeyData before.
         hostnonce (str)
           8 bytes random binary data
         Returns
           device nonce (str), another 8 bytes random data
        """
        if len(hostnonce) != 8:
            raise ValueError('Supplied host nonce length wrong')
        reply = self.__send_query('1800 080046 f0030103 20 ff 000000 %*', hostnonce)
        return self.__parse_response(reply, '1800 080046 f0030103 20 00 000000 %*')[0]

    def forget_session_key(self):
        """
         Invalidate the session key established by nonce exchange.
         Does not invalidate the root key set up by sendKeyData.
        """
        reply = self.__send_query('1800 080046 f0030103 21 ff 000000')
        return self.__parse_response(reply, '1800 080046 f0030103 21 00 000000')

    #
    # Downloads
    #

    def setup_download(self, sessionkey):
        """
         Prepare the download of a music track to the device.
         sessionkey (str)
           8 bytes DES key used for securing the current session, the key
           has to be calculated by the caller from the data exchanged in
           sessionKeyExchange and the root key selected by sendKeyData
        """
        if len(sessionkey) != 8:
            raise ValueError('Supplied Session Key length wrong')

        iv = create_iv()
        encrypter = DES.new(sessionkey, DES.MODE_CBC, iv)

        padding = (4 * '\1').encode('utf-8')
        encryptedarg_bytes = encrypter.encrypt(padding + NetMD.__CONTENT_ID + KEK)
        encryptedarg_str = bytes_to_str(encryptedarg_bytes)

        reply = self.__send_query('1800 080046 f0030103 22 ff 0000 %*', encryptedarg_str)
        return self.__parse_response(reply, '1800 080046 f0030103 22 00 0000')

    def commit_track(self, tracknum, sessionkey):
        """
         Commit a track. The idea is that this command tells the device
         that the license for the track has been checked out from the
         computer.
         track (int)
           Track number returned from downloading command
         sessionkey (str)
           8-byte DES key used for securing the download session
        """
        if len(sessionkey) != 8:
            raise ValueError('Supplied Session Key length wrong')
        encrypter = DES.new(sessionkey, DES.MODE_ECB)
        authentication = encrypter.encrypt(create_iv())
        reply = self.__send_query('1800 080046 f0030103 48 ff 00 1001 %w %*',
                                  tracknum, bytes_to_str(authentication))
        return self.__parse_response(reply, '1800 080046 f0030103 48 00 00 1001 %?%?')

    def send_track(self, wireformat, diskformat, frames, pktcount, packets, sessionkey):
        """
         Send a track to the NetMD unit.
         wireformat (int)
           The format of the data sent over the USB link.
           one of WIREFORMAT_PCM, WIREFORMAT_LP2, WIREFORMAT_105KBPS or
           WIREFORMAT_LP4
         diskformat (int)
           The format of the data on the MD medium.
           one of DISKFORMAT_SP_STEREO, DISKFORMAT_LP2 or DISKFORMAT_LP4.
         frames (int)
           The number of frames to transfer. The frame size depends on
           the wire format. It's 2048 bytes for WIREFORMAT_PCM, 192 bytes
           for WIREFORMAT_LP2, 152 bytes for WIREFORMAT_105KBPS and 92 bytes
           for WIREFORMAT_LP4.
         pktcount (int)
           Number of data packets to send (needed to calculate the raw
           packetized stream size
         packets (iterator)
           iterator over (str, str, str), with the first string being the
           encrypted DES encryption key for this packet (8 bytes), the second
           the IV (8 bytes, too) and the third string the encrypted data.
         sessionkey (str)
           8-byte DES key used for securing the download session
         Returns
           A tuple (tracknum, UUID, content ID).
           tracknum (int)
             the number the new track got.
           UUID (str)
             an 8-byte-value to recognize this track for check-in purpose
           content ID
             the content ID. Should always be the same as passed to 
             setupDownload, probably present to prevent some attack vectors
             to the DRM system.
        """
        if len(sessionkey) != 8:
            raise ValueError('Supplied Session Key length wrong')

        totalbytes = WIRE_TO_FRAME_SIZE[wireformat] * frames + pktcount * 24;

        reply = self.__send_query('1800 080046 f0030103 28 ff 000100 1001' \
                                  'ffff 00 %b %b %d %d',
                                  wireformat, diskformat, frames, totalbytes)
        self.__parse_response(reply, '1800 080046 f0030103 28 00 000100 1001 %?%? 00'\
                              '%*')

        for (key, iv, data) in packets:
            binpkt = pack('>Q',len(data)) + key + iv + data
            self.net_md_usb.writeBulk(binpkt)

        reply = self.__read_reply()
        self.net_md_usb._getReplyLength()

        (track, encryptedreply) = \
          self.__parse_response(reply, '1800 080046 f0030103 28 00 000100 1001 %w 00' \
                                '%?%? %?%?%?%? %?%?%?%? %*')
        iv = create_iv()
        encrypter = DES.new(sessionkey, DES.MODE_CBC, iv)
        replydata = encrypter.decrypt(str_to_bytearray(encryptedreply))

        return (track, replydata[0:8], replydata[12:32])

    def disable_new_track_protection(self, val):
        """
         NetMD downloaded tracks are usually protected from modification
         at the MD device to prevent loosing the check-out license. This
         setting can be changed on some later models to have them record
         unprotected tracks, like Simple Burner does.
         The setting stays in effect until endSecureSession, where it
         is reset to 0.
         val (int)
           zero enables protection of future downloaded tracks, one
           disables protection for these tracks.
        """
        reply = self.__send_query('1800 080046 f0030103 2b ff %w', val)
        return self.__parse_response(reply, '1800 080046 f0030103 2b 00 %?%?')

    #
    # Private routines, data to/from NetMD
    #

    def __send_query(self, query_format, *query_args):
        query = [NetMD.__STATUS_CONTROL, ] + self.__format_query(query_format, *query_args)
        binquery = bytes_to_str(query)

        self.net_md_usb.sendCommand(query)

        return self.__read_reply()

    def __read_reply(self):
        result = self.net_md_usb.readReply()
        status = result[0]
        if status == NetMD.__STATUS_NOT_IMPLEMENTED:
            raise NetMDNotImplemented('Not implemented')
        elif status == NetMD.__STATUS_REJECTED:
            raise NetMDRejected('Rejected')
        elif status not in (NetMD.__STATUS_ACCEPTED, NetMD.__STATUS_IMPLEMENTED,
                            NetMD.__STATUS_INTERIM):
            raise NotImplementedError('Unknown returned status: %02X' %
                (status, ))
        return result[1:]

    def __format_query(self, format, *args):
        result = []
        append = result.append
        extend = result.extend
        half = None
        def hexAppend(value):
            append(int(value, 16))
        escaped = False
        arg_stack = list(args)
        for char in format:
            if escaped:
                escaped = False
                value = arg_stack.pop(0)
                if char in NetMD.__FORMAT_TYPE_LEN_DICT:
                    for byte in range(NetMD.__FORMAT_TYPE_LEN_DICT[char] - 1, -1, -1):
                        append((value >> (byte * 8)) & 0xff)
                # String ('s' is 0-terminated, 'x' is not)
                elif char in ('s', 'x'):
                    length = len(value)
                    if char == 'x':
                        append((length >> 8) & 0xff)
                        append(length & 0xff)
                    extend(ord(x) for x in value)
                elif char == '*':
                    extend(ord(x) for x in value)
                else:
                    raise ValueError('Unrecognised format char: %r' % (char, ))
                continue
            if char == '%':
                assert half is None
                escaped = True
                continue
            if char == ' ':
                continue
            if half is None:
                half = char
            else:
                hexAppend(half + char)
                half = None
        assert len(arg_stack) == 0
        return result

    def __parse_response(self, response, format):
        result = []
        append = result.append
        half = None
        escaped = False
        input_stack = list(response)
        def pop():
            return input_stack.pop(0)
        for char in format:
            if escaped:
                escaped = False
                if char == '?':
                    pop()
                    continue
                if char in NetMD.__FORMAT_TYPE_LEN_DICT:
                    value = 0
                    for byte in range(NetMD.__FORMAT_TYPE_LEN_DICT[char] - 1, -1, -1):
                        value |= (pop() << (byte * 8))
                    append(value)
                # String ('s' is 0-terminated, 'x' is not)
                elif char in ('s', 'x'):
                    length = pop() << 8 | pop()
                    value = ''.join(input_stack[:length])
                    input_stack = input_stack[length:]
                    if char == 's':
                        append(value[:-1])
                    else:
                        append(value)
                # Fetch the remainder of the response in one value
                elif char == '*':
                    value = bytes_to_str(input_stack)
                    input_stack = []
                    append(value)
                else:
                    raise ValueError('Unrecognised format char: %r' % (char, ))
                continue
            if char == '%':
                assert half is None
                escaped = True
                continue
            if char == ' ':
                continue
            if half is None:
                half = char
            else:
                input_value = pop()
                format_value = int(half + char, 16)
                if format_value != input_value:
                    raise ValueError('Format and input mismatch at %i: '
                        'expected %02x, got %02x' % (
                            len(response) - len(input_stack) - 1,
                            format_value, input_value))
                half = None
        assert len(input_stack) == 0
        return result


sys.modules[__name__] = iter(NetMDDevicesModule())
