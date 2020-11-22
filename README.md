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
### storing time data
```bash
sudo apt-get install build-essential python3-dev
```


## Setting up InfluxDb
```bash
sudo wget -O - https://packages.grafana.com/gpg.key | apt-key add -
sudo wget -O - https://repos.influxdata.com/influxdb.key | apt-key add -

wget -qO- https://repos.influxdata.com/influxdb.key | sudo tee /etc/apt/sources.list.d/influxdb.list test $VERSION_ID = "8" && echo "deb https://repos.influxdata.com/debian jessie stable" | sudo tee /etc/apt/sources.list.d/influxdb.list test $VERSION_ID = "9" && echo "deb https://repos.influxdata.com/debian stretch stable" | sudo tee /etc/apt/sources.list.d/influxdb.list 

sudo apt-get update && sudo apt-get install influxdb 
sudo service influxdb start 

#verify influxdb is running with the following command. 
sudo service influxdb status 
```


### Grafana

Open: http://192.168.0.17:3000/login with admin:admin
Setup influx dbas data source: http://192.168.0.17:3000/datasources
> your local influx db url is http://localhost:8086 and the db name is temperature
Save :)

raw influxdb example query for grafana:
```
SELECT mean("temperature") FROM "boiler_temperature" WHERE (sensor=1) and $timeFilter GROUP BY time($__interval) fill(previous)
```

