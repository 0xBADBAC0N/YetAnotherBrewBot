# YetAnotherBrewBot

## SD Card setup
### get sd card
> sudo fdisk -l

### unmount
> sudo umount /dev/sdc1
>  sudo umount /dev/sdc2

### backup current image
> sudo dd if=/dev/sdc of=retropi_sd_card_copy.img

#### to revert the backup do
> sudo dd if=retropi_sd_card_copy.img of=/dev/sdc

## Temeprature sensors setup
https://www.amazon.de/dp/B018GQN5HE
```
 sudo nano /etc/udev/rules.d/99-myhid.rules
 KERNEL=="hidraw*", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="480",  MODE="0666", GROUP="plugdev", TAG+="uaccess", TAG+="udev-acl"
sudo addgroup plugdev
sudo usermod -aG plugdev hendrik
sudo udevadm control --reload-rules
pip3 install pyusb
```
test code
```
import os
import sys
import usb.core
import usb.util
import struct
import time

# find our device
dev = usb.core.find(idVendor=0x16C0, idProduct=0x0480)

if dev is None:
    raise ValueError('Device is not found')

# Attach and detach the usb
if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

#print("Device found")
#print(dev)
cfg = dev.get_active_configuration()
#print("Config found")
#print(cfg)
intf = cfg[(0, 0)]
while True:
    data = dev.read(0x81, 64, 2000)
    unpacked = struct.unpack('<H', bytes(data[4:6]))
    temp = unpacked[0] / 10
    pwr = 'E' if data[2] == 1 else 'P'
    print('sensor %d of %d: %+.1f degC (pwr: %s)' % (data[0], data[1], temp, pwr))
    time.sleep(1)
```

