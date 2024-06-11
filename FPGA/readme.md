# Setup Instructions for DE10-Nano
- Building the necessary libraries for DE10 Nano board must be done with:
  - a pc with an intel processor running linux
  - lubuntu is lite ubuntu which is for comps with limited cpu ability
  - around 35GB of space for the nix store
- The development environment for this project was setup on a [Wo-We Mini PC](https://www.amazon.com/dp/B0CLD8JRWK?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- Processor used for this: Intel Celeron N4020 CPU @ 1.1GHz x 2 running [lubuntu 24.04 64 bit](https://lubuntu.me/downloads/)

---

### 1. Installing Nix 
   - [Nix Website](https://nixos.org/download/#nixos-iso)
   - Browsing for Nix Packages [Package Search Website](https://search.nixos.org/packages?ref=itsfoss.com)

Adding the flake feature
```zsh
sudo mkdir /etc/nix
sudo nano /etc/nix/nix.conf
```
- Add this to the config file
- the first line is most important
~~~
# Nix Config File

# enable flake feature
experimental-features = nix-command flakes

# specifies which users are trusted by the Nix daemon
trusted-users = @root

# automatically optimize the store by deduplicating files
# performing other optimizations to reduce disk usage and improve performance
auto-optimise-store = true
~~~

---

### 2. Download Repo from Github
- This is an already made NixOS system for the DE10

```zsh
git clone https://github.com/tpwrules/papa_fpga.git
```

cd into folder

---

### 3. Build SD Card Image for DE10
- this can only be performed on an intel processor with nix installed
- this only needs to be done once
- then updates can be run from the device itself with ```nix rebuild``` command

- run the command:
```zsh
nix build .#nixosConfigurations.de10-nano -j1 -L
```
- -j1 is for small cpu computers
- -L is to see a verbose output as it builds
- this will take some time the first time (8+ hours potentially)
- there is no harm in stopping the build and restarting it
- it could potentially reduce memory if needed 
- might run into memory issues when building
  - google how to make swap memory bigger
---

### 4. Create Bootable Drive
- this can be done on any computer

- the build command will make a folder called "result"

- inside that folder is sd-image folder
- inside that is a .img.zst file

- use etcher to put that onto the SD card 
- you can also use zstdcat/dd
   - this decompresses the image and writes it to the SD card

#### 4.1: zstdcat/dd terminal method
1. Insert SD card into computer
2. Identify sd card's device name
   - not the mount point of the SD card, but the device name
```zsh
lsblk 
```
   - the name that corresponds with the mount point / SD card name
   - mine is 'mmcblk1'

3. Unmount the SD card (if it's mounted)
   - it wont hurt to do this if you're not sure
```zsh
sudo umount /dev/mmcblk1
```
4. Decompress and Write Image
   - *Warning:* incorrect use of ```dd``` commands could destroy your computer's internal disk, so use with care
```zsh
sudo apt install zstd
```
```zsh
zstdcat result/sd-image/*.img.zst | sudo dd of=/dev/mmcblk1 bs=4M status=progress conv=fsync
```
- if you eject the sd card when it's done and reinsert it, it should say NixOS as the sd card name

---

### 5. Starting up the DE10
- put the SD card in the DE10
- set de10 mel switches to all 0 (up)
- connect to the de10 through the UART mini usb connector
- plug the power cable to the DE10

There are two ways we will connect to the DE10:
1. connection over UART 
2. connection via ssh with ethernet over usb 
    
---

#### 5.1: UART Connection on Linux
```zsh
sudo apt install minicom
```
- Sometimes, you might need appropriate permissions to access these devices
- You can change the permissions by adding your user to the dialout group
```zsh
sudo usermod -aG dialout kevmck
```
- program that tries to find modems on serials ports so get rid of it
```zsh
sudo apt purge modemmanager
```
- start the UART connection
- most likely USB0, but maybe USB1
```zsh
minicom -D /dev/ttyUSB0 -b 115200
```
- once run, you should see start up of device
- to exit session: press control a, let go of both, press x

---

#### 5.2: SSH Connection
```zsh

```







