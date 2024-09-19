# App Info

## Powering On
- when the phased array is powered on, it takes about a minute to fully start up


 

## Monitoring the FPGA and Pi during run
```zsh
ssh admin@192.168.1.1 
journalctl -fu temp-sensor-server
```


```zsh
ssh nixos@192.168.1.201
journalctl -fu start-mic-server
```



- if pi is plugged campus ethernet and wifi is connected on laptop
```zsh
ssh admin@pi-nix.uom.memphis.edu   
```


```zsh
sudo nano /etc/resolv.conf
```
~~~
nameserver 8.8.8.8
~~~