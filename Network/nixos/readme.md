# Loading and Building Networking NixOS for Raspberry Pi

## Initial Setup
- you will need to build nixos sd card image on a processor that the device will be running on
- for this, we will be using a raspberry pi to build
- so to start out we need to get any nixos working on the pi so we can build a custom sd_card image
- once you have an sd image built from a custom configuration.nix file you can 
  - then ssh into the device
  - download a git repo with your config files
  - rebuild the nixos in place without having to shutdown
  
### Steps for Initial Setup
-On the Raspberry Pi
- install a premade version of nix for pi
- [Tutorial](https://mtlynch.io/nixos-pi4/)

```zsh
sudo nixos-channel --update
nixos-env -iA nixos.git
```
- [YouTube Tutorial](https://www.youtube.com/watch?v=VIuPRL6Ucgk&list=WL&index=4)
```zsh
git clone https://github.com/kevmck451/phase_array_fossn.git
```
```zsh
cd phase_array_fossn/Network/nixos/sd-image
```
```zsh
sudo nixos build --extra-experimental-features nixos-command --extra-experimental-features flakes .#packages.aarch64-linux.sdcard
```

### On Mac
```zsh
scp nixos@192.168.0.137:~/phase_array_fossn/Network/nixos/sd-image/flake.lock ~/Downloads/
```
scp nixos@192.168.0.143:~/etc/nixos/hardware-configuration.nix ~/Downloads/
```zsh
scp -r nixos@192.168.0.137:~/phase_array_fossn/Network/nixos/sd-image/result ~/Downloads/
```
- remove sd card from pi and flash with new sd card image
```zsh
cd phase_array_fossn/Network/nixos/sd-image
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
nixos-channel --update
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
- move the file manually (optional)
```zsh
cd /home/admin/phase_array_fossn
git pull origin main
sudo cp /home/admin/phase_array_fossn/Network/nixos/configuration.nixos /etc/nixos/configuration.nix
sudo cp /home/admin/phase_array_fossn/Network/nixos/hardware-configuration.nix /etc/nixos/hardware-configuration.nix
sudo nixos-rebuild switch
```
- create a symlink to config file 
```zsh
sudo rm /etc/nixos/configuration.nix
sudo rm /etc/nixos/hardware-configuration.nix
sudo ln -s /home/admin/phase_array_fossn/Network/nixos/configuration.nix /etc/nixos/configuration.nix
sudo ln -s /home/admin/phase_array_fossn/Network/nixos/hardware-configuration.nix /etc/nixos/hardware-configuration.nix
```
- check for errors before installing
```zsh
sudo nixos-rebuild dry-run
```





```zsh
ssh admin@pi-nixos.local  
```
- pi IP on school: 141.225.162.166
- pi IP at home: 192.168.0.137


```zsh

```
