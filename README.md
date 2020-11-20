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
```bash
apt-get install libusb-dev
 sudo nano /etc/udev/rules.d/99-myhid.rules
 KERNEL=="hidraw*", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="480",  MODE="0666", GROUP="plugdev", TAG+="uaccess", TAG+="udev-acl"
sudo addgroup plugdev
sudo usermod -aG plugdev hendrik
sudo udevadm control --reload-rules
pip3 install pyusb
```
test code
```python
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


### storing time data
```bash
sudo apt-get install build-essential python3-dev
```

```python
#! /usr/local/bin/python3.8
import os
import sys
import usb.core
import usb.util
import struct
import time
import logging 

logging.basicConfig(filename='/var/log/temperature.log', filemode='a', format='%(created)f %(message)s', level=logging.INFO) 
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
    logging.info('SensorAmount=%d and Sensor=%d and Temp=%.1f and Power=%s' % (data[0], data[1], temp, pwr))
    time.sleep(1)
```

## Setting up InfluxDb and telegraf
```bash
sudo wget -O - https://packages.grafana.com/gpg.key | apt-key add -
sudo wget -O - https://repos.influxdata.com/influxdb.key | apt-key add -

wget -qO- https://repos.influxdata.com/influxdb.key | sudo tee /etc/apt/sources.list.d/influxdb.list test $VERSION_ID = "8" && echo "deb https://repos.influxdata.com/debian jessie stable" | sudo tee /etc/apt/sources.list.d/influxdb.list test $VERSION_ID = "9" && echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list 

sudo apt-get update && sudo apt-get install influxdb 
sudo service influxdb start 

#verify influxdb is running with the following command. 
sudo service influxdb status 
```
### TELGRAF LOG PARSER INSTALLATION ON RASPBERRY PI
```bash
 wget https://dl.influxdata.com/telegraf/releases/telegraf_1.16.2-1_armhf.deb
 sudo dpkg -i telegraf_1.16.2-1_armhf.deb
```

### PARSING LOGS ON RASPBERRY PI USING TELEGRAF
```bash
mkdir -p /etc/telegraf/config
touch /etc/telegraf/config/temperatureLog.conf
```

temperatureLog.conf
```
[agent]
   # Batch size of values that Telegraf sends to output plugins.
   metric_batch_size = 1000
   # Default data collection interval for inputs.
   interval = "10s"
   # Added degree of randomness in the collection interval.
   collection_jitter = "5s"
   # Send output every 5 seconds
   flush_interval = "5s"
   # Buffer size for failed writes.
   metric_buffer_limit = 10000
   # Run in quiet mode, i.e don't display anything on the console.
   quiet = true
 
# Read metrics about cpu usage
[[inputs.cpu]]
   ## Whether to report per-cpu stats or not
   percpu = false
   ## Whether to report total system cpu stats or not
   totalcpu = true
   ## If true, collect raw CPU time metrics.
   collect_cpu_time = false
   ## If true, compute and report the sum of all non-idle CPU states.
   report_active = false

[[inputs.logparser]]
   ## file(s) to read:
   files = ["/var/log/temperature.log"]
    
   # Only send these fields to the output plugins
   fieldpass = ["sensoramount", "sensor", "temperature", "power"]
   tagexclude = ["path"]

   # Read the file from beginning on telegraf startup.
   from_beginning = true
   name_override = "boiler_temperature"

   ## For parsing logstash-style "grok" patterns:
   [inputs.logparser.grok]
     patterns = ["%{TEMPERATURE_PATTERN}"]
     custom_patterns = '''TEMPERATURE_PATTERN %{{TIMESTAMP_ISO8601:timestamp} SensorAmount=%{NUMBER:sensoramount:int} and Sensor=%{NUMBER:sensor:int} and Temp=%{NUMBER:temperature:float}%{GREEDYDATA}'''

[[outputs.influxdb]]
   ## The full HTTP or UDP URL for your InfluxDB instance.
   urls = ["http://127.0.0.1:8086"] # required
   
   ## The target database for metrics (telegraf will create it if not exists).
   database = "temperature" # required
   
   ## Name of existing retention policy to write to.  Empty string writes to
   ## the default retention policy.
   retention_policy = ""
   ## Write consistency (clusters only), can be: "any", "one", "quorum", "all"
   write_consistency = "any"
   
   ## Write timeout (for the InfluxDB client), formatted as a string.
   ## If not provided, will default to 5s. 0s means no timeout (not recommended).
   timeout = "10s"
   # username = "telegraf"
   # password = "metricsmetricsmetricsmetrics"
   ## Set the user agent for HTTP POSTs (can be useful for log differentiation)
   # user_agent = "telegraf"
   ## Set UDP payload size, defaults to InfluxDB UDP Client default (512 bytes)
   # udp_payload = 512

```
start also in background `telegraf --config /etc/telegraf/config/temperatureLog.conf`

### Installing Grafana and creating dashboards on the Raspberry Pi
```bash
sudo sed -i '2 s/^/# /' /etc/apt/sources.list
sudo apt-get install grafana
sudo service grafana-server start
```
Open: http://192.168.0.17:3000/login with admin:admin
Setup influx dbas data source: http://192.168.0.17:3000/datasources
> your local influc db url is http://localhost:8086 and the db name is temperature
Save :)

raw influxdb querie for grafana:
```
SELECT mean("temperature") FROM "boiler_temperature" WHERE sensor=1 and $timeFilter GROUP BY time($__interval) fill(previous)
```

