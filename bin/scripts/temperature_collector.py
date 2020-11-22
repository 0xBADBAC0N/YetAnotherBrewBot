#! /usr/local/bin/python3.8
import struct
import time
import usb.util
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086)
client.create_database('temperature')
measurement_name = 'boiler_temperature'

dev = usb.core.find(idVendor=0x16C0, idProduct=0x0480)

if dev is None:
    raise ValueError('Device is not found')

if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]

points = []
while True:
    data = dev.read(0x81, 64, 2000)
    unpacked = struct.unpack('<H', bytes(data[4:6]))
    temp = unpacked[0] / 10
    pwr = 'E' if data[2] == 1 else 'P'

    points.append(
        {
            "measurement": measurement_name,
            "tags": {
                "sensor": int(data[1]),
                "power": pwr
            },
            "fields": {
                "sensoramount": int(data[0]),
                "temperature": float(temp),
            },
            "time": int((time.time() * 1000))
        }
    )
    if len(points) >= 4:
        client.write_points(points, database='temperature', time_precision='ms', batch_size=10000, protocol='json')
        data = []
    time.sleep(1)
