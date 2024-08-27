# Temp Sensor: BME280

## Physical Connection
- Using 4 pin 1/8" audio jack for connector (TRRS)
4: tip: 3.3V
3: ring 1: scl
2: ring 2: gnd
1: sleeve: sda



#### confirming the address  
```zsh
# nix environment 
nix-shell -p i2c-tools

# read buses
i2cdetect 0
i2cdetect 1
i2cdetect 2
i2cdetect 3
i2cdetect 4
```
- 3 was the only one with a single address at 76
~~~
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- 76 --    
~~~






#### test script
- python console to run example script from [Github](https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/2)



#### Get all libraries into nix so it can build them for access in scripts
https://github.com/rm-hull/bme280
https://github.com/rm-hull/bme280/tags


#### add script to automatic start up with Nix

- check output of print statements
```zsh
journalctl -fu temp-sensor
```
```zsh
journalctl -fu temp-sensor-server
```
```zsh
journalctl -fu start-mic-server
```


#### gitpull 
```zsh
sudo -s
sudo nano /etc/resolv.conf
```
~~~
change nameserver = 8.8.8.8
~~~

