# Loading and Building Networking NixOS for Raspberry Pi

## On the Raspberry Pi
- install a premade version of nix for pi
- [Tutorial](https://mtlynch.io/nixos-pi4/)

```zsh
sudo nix-channel --update
nix-env -iA nixos.git
```
- [YouTube Tutorial](https://www.youtube.com/watch?v=VIuPRL6Ucgk&list=WL&index=4)
```zsh
git clone https://github.com/kevmck451/phase_array_fossn.git
```
```zsh
cd phase_array_fossn/Network/nix/pi_sdcard
```
```zsh
sudo nix build --extra-experimental-features nix-command --extra-experimental-features flakes .#packages.aarch64-linux.sdcard
```

## On Mac
```zsh
scp nixos@192.168.0.137:~/phase_array_fossn/Network/nix/pi_sdcard/flake.lock ~/Downloads/
```
```zsh
scp -r nixos@192.168.0.137:~/phase_array_fossn/Network/nix/pi_sdcard/result ~/Downloads/
```
- remove sd card from pi and flash with new sd card image
```zsh
cd phase_array_fossn/Network/nix/pi_sdcard
```
```zsh
zstd -d result/sd-image/*.img.zst -o ~/Downloads/extracted_image.img        
```
- use belena etcher to flash to sd card
- put back in pi and start up
- find pi's ip address from router
- ssh into nixos pi
```zsh
ssh admin@192.168.0.137    
```
- enter password
- switch to root user
```zsh
sudo -s
```
```zsh
nix-channel --update
```
```zsh
nixos-generate-config
```
```zsh
nano /etc/nixos/configuration.nix
```
- everything is in the pi_config.nix file
```zsh
passwd admin
```
- choose password: nix
```zsh
nixos-rebuild switch
```
```zsh
arp -a   
```
- after disconnection from ssh, i had to unplug pi and plug back in
```zsh
arp -a   
```
- ssh into pi
```zsh
ssh admin@192.168.0.137
```
```zsh
git clone https://github.com/kevmck451/phase_array_fossn.git
```
```zsh
cd /home/admin/phase_array_fossn
git pull origin main
sudo cp /home/admin/phase_array_fossn/Network/nix/pi_config.nix /etc/nixos/configuration.nix
sudo nixos-rebuild switch
```

```zsh

```




```zsh

```
