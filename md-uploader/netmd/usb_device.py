"""NetMD USB interface

This module defines lower-level interaction with NetMD devices via USB. Those
calling the module should not concern themselves with USB at all.

The module itself is iterable. Getting all supported devices is as simple as:
```
import devices

for netmd in devices:
    # do something with the device, e.g. pass to higher level interface
    libnetmd.NetMDInterface(netmd)

```
"""

from io import StringIO
import sys
from time import sleep

import libusb1
import usb1

from .constants import KNOWN_USB_ID_SET


class USBDevicesModule(object):
    def __init__(self):
        self.usb_context = usb1.USBContext()

    def __iter__(self):
      """
        Iterator for plugged-in NetMD devices.

        Returns (yields) NetMD instances.
      """
      for device in self.usb_context.getDeviceList():
          if (device.getVendorID(), device.getProductID()) in KNOWN_USB_ID_SET:
              yield NetMDUSB(device.open())


class NetMDUSB(object):
    """
      Low-level interface for a NetMD device.
    """

    __BULK_WRITE_ENDPOINT = 0x02

    def __init__(self, usb_handle, interface=0):
        """
          usb_handle (usb1.USBDeviceHandle)
            USB device corresponding to a NetMD player.
          interface (int)
            USB interface implementing NetMD protocol on the USB device.
        """
        self.usb_handle = usb_handle
        self.interface = interface
        usb_handle.setConfiguration(1)
        usb_handle.claimInterface(interface)
        if self._getReplyLength() != 0:
            self.readReply()


    def __del__(self):
        try:
            self.usb_handle.resetDevice()
            self.usb_handle.releaseInterface(self.interface)
        except: # Should specify an usb exception
            pass

    def _getReplyLength(self):
        reply = self.usb_handle.controlRead(libusb1.LIBUSB_TYPE_VENDOR | \
                                            libusb1.LIBUSB_RECIPIENT_INTERFACE,
                                            0x01, 0, 0, 4)
        return reply[2]

    def sendCommand(self, command):
        """
          Send a raw binary command to device.
          command (str)
            Binary command to send.
        """
        self.usb_handle.controlWrite(libusb1.LIBUSB_TYPE_VENDOR | \
                                     libusb1.LIBUSB_RECIPIENT_INTERFACE,
                                     0x80, 0, 0, command)

    def readReply(self):
        """
          Get a raw binary reply from device.
          Returns the reply.
        """
        reply_length = 0
        while reply_length == 0:
            reply_length = self._getReplyLength()
            if reply_length == 0:
                sleep(0.1)
        reply = self.usb_handle.controlRead(libusb1.LIBUSB_TYPE_VENDOR | \
                                            libusb1.LIBUSB_RECIPIENT_INTERFACE,
                                            0x81, 0, 0, reply_length)
        return reply

    def writeBulk(self, data):
        """
          Write data to device.
          data (str)
            Data to write.
        """
        self.usb_handle.bulkWrite(NetMDUSB.__BULK_WRITE_ENDPOINT, data)


sys.modules[__name__] = iter(USBDevicesModule())
