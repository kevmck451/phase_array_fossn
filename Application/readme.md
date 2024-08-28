


## Monitoring the FPGA and Pi during run

```zsh
ssh admin@192.168.1.1 
journalctl -fu temp-sensor-server
```


```zsh
ssh nixos@192.168.1.201
journalctl -fu start-mic-server
```