#!/usr/bin/env bash


apt upgrade
echo '---- Setup working folder'
sudo mkdir -p /opt/yabb/configs/telegraf
sudo mkdir -p /opt/yabb/scripts

sudo cp configs/temperatureLog.conf /opt/yabb/configs/telegraf/temperatureLog.conf
sudo cp scripts/temperature_collector.py /opt/yabb/scripts/temperature_collector.py


echo '---- Setup UDEV rules RW for usb rawHID devide'
echo 'KERNEL=="hidraw*", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="480",  MODE="0666", GROUP="plugdev", TAG+="uaccess", TAG+="udev-acl"' > /tmp/99-myhid.rules
sudo cp /tmp/99-myhid.rules /etc/udev/rules.d/99-myhid.rules
sudo addgroup plugdev
sudo usermod -aG plugdev "$USER"
sudo udevadm control --reload-rules


echo '---- Setup pyusb'
apt-get install libusb-dev install build-essential python3-dev
pip3 install pyusb


echo '---- Setup InfluxDB'
cd /tmp

sudo wget -O - https://packages.grafana.com/gpg.key | apt-key add -
sudo wget -O - https://repos.influxdata.com/influxdb.key | apt-key add -

wget -qO- https://repos.influxdata.com/influxdb.key | \
  sudo tee /etc/apt/sources.list.d/influxdb.list test $VERSION_ID = "8" \
  && echo "deb https://repos.influxdata.com/debian jessie stable" \
  | sudo tee /etc/apt/sources.list.d/influxdb.list test $VERSION_ID = "9" \
  && echo "deb https://repos.influxdata.com/debian stretch stable" \
  | sudo tee /etc/apt/sources.list.d/influxdb.list

sudo apt-get update && sudo apt-get install influxdb
sudo service influxdb start
sudo service influxdb status


echo '---- Setup Telegraf'
wget https://dl.influxdata.com/telegraf/releases/telegraf_1.16.2-1_armhf.deb
sudo dpkg -i telegraf_1.16.2-1_armhf.deb


echo '---- Setup Grafana'
# clean up duplicates in rpi sources
sudo sed -i '2 s/^/# /' /etc/apt/sources.list
sudo apt install grafana


echo '---- Start processes'
sudo screen -dmS telegraf bash -c './opt/yabb/scripts/temperature_collector.py; exec bash'
sudo screen -dmS telegraf bash -c 'telegraf --config /opt/yabb/configs/telegraf/temperatureLog.conf; exec bash'
sudo service grafana-server start


