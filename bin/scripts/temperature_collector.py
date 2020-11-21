#! /usr/local/bin/python3.8
import logging
import struct
import time
import usb.util
import tempfile
import os

logging.basicConfig(filemode='a')
logger = logging.getLogger(__name__)

handler = tempfile.NamedTemporaryFile(prefix='temperature_', dir='/var/log/temperature/')
os.fchmod(handler.fileno(), 0o640)
formatter = logging.Formatter(fmt='%(asctime)s %(message)s')
fh = logging.FileHandler(handler.name)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.setLevel(logging.INFO)
logger.propagate = False

dev = usb.core.find(idVendor=0x16C0, idProduct=0x0480)

if dev is None:
    raise ValueError('Device is not found')

if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]

while True:
    data = dev.read(0x81, 64, 2000)
    unpacked = struct.unpack('<H', bytes(data[4:6]))
    temp = unpacked[0] / 10
    pwr = 'E' if data[2] == 1 else 'P'
    logger.info('SensorAmount=%d and Sensor=%d and Temp=%.1f and Power=%s' % (data[0], data[1], temp, pwr))
    time.sleep(1)
