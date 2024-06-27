# Setup and Maintenance for the DE10-Nano
1. First Time Setup Instructions
2. Interacting with the DE10-Nano

---
# 1. First Time Setup Instructions
- Building the necessary files for operating the DE10 Nano must be done with:
  - a pc with an intel processor running linux
  - Ubuntu is recommended, but other variants like lubuntu can work
  - lubuntu is lite ubuntu which is for computers with limited cpu ability
- This process was tested on a [Wo-We Mini PC](https://www.amazon.com/dp/B0CLD8JRWK?psc=1&ref=ppx_yo2ov_dt_b_product_details)
  - it worked but was very slow and needed special consideration with some aspects of the nix builds 
  - It's processor is an Intel Celeron N4020 CPU @ 1.1GHz x 2 (4GB RAM) running [lubuntu 24.04 64 bit](https://lubuntu.me/downloads/)
- It was also test with a [GMKtec Mini PC](https://www.amazon.com/gp/product/B0B75PT2RY/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1)
  - processor is an Intel 11th Gen N5105 @ 3.4GHz x 4 (8GB RAM) running [Ubuntu 20.04.6](https://releases.ubuntu.com/focal/)


---
## Programming Environment Setup

### Computer Requirements
- recommended minimum computer requirements
  - having two cores and 4GB memory with swap memory at 16GB is theoretically possible
  - four cores with 8GB memory and 12GB swap memory took 10+hrs to build for the first time

---
### Installing Necessary Libraries
- htop: used to monitor computer during builds
```zsh
sudo apt install htop
```
- git: updating code repository after changes
```zsh
sudo apt install git
```
- wormhole: easily transfer files over the network without needing an IP
```zsh
sudo apt install magic-wormhole
```
- curl: used to install nix / copies files from a url
```zsh
sudo apt install curl
```
- nix: environment shells / NixOS builds / etc
```zsh
sudo apt install nix
```
- ifconfig: used to see device's network information (specifically IP address)
```zsh
sudo apt install net-tools
```
- ssh: allows you to "login" to other computers and control them from the terminal
```zsh
sudo apt install openssh-server
```
- zstd: for decompressing .zst files
```zsh
sudo apt install zstd
```
- minicom: used to communicate with devices through UART
```zsh
sudo apt install minicom
```
- Sometimes, you might need appropriate permissions to access these devices
- You can change the permissions by adding your user to the dialout group
- kevmck would be replaced with your username
```zsh
sudo usermod -aG dialout kevmck
```
- program that tries to find modems on serials ports so get rid of it
```zsh
sudo apt purge modemmanager
```

---
### Increasing Swap Memory
What is Swap Memory and why it's important
- check current swap memory size with htop or this;
```zsh
sudo swapon --show
```
- disable current swap file temporarily
```zsh
sudo swapoff /swapfile
```
- resize the swap file to 12GB
```zsh
sudo dd if=/dev/zero of=/swapfile bs=1M count=12288
```
- set the correct permissions
```zsh
sudo chmod 600 /swapfile
```
- setup the swap area
```zsh
sudo mkswap /swapfile
```
- enable the swap file
```zsh
sudo swapon /swapfile
```
- you should see the swap changing in htop but can also check with this:
```zsh
sudo swapon --show
```
- Edit the '/etc/fstab' file to ensure the swap file is used at boot
```zsh
sudo nano /etc/fstab
```
- add or update the following line to ensure it reads:
~~~
/swapfile none swap sw 0 0
~~~


---
### 1. Installing Nix 
   - [Nix Website](https://nixos.org/download/#nixos-iso)
   - Browsing for Nix Packages [Package Search Website](https://search.nixos.org/packages?ref=itsfoss.com)


Multi-user installation for Linux
```zsh
sh <(curl -L https://nixos.org/nix/install) --daemon
```

- Adding the flake feature
- the folder might already exist
```zsh
sudo mkdir /etc/nix
sudo nano /etc/nix/nix.conf
```
- Add this to the config file
- the first line is most important
- if there's something already there, delete it
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
git clone https://github.com/kevmck451/phase_array_fossn.git 
```
- cd into folder

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
- might run into 'lack of disk space' error
  - this might be due to tmp space not big enough
  - google remount /tmp with larger size
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
zstdcat result/sd-image/*.img.zst | sudo dd of=/dev/mmcblk1 bs=4M status=progress conv=fsync
```
- if you eject the sd card when it's done and reinsert it, it should say NixOS as the sd card name

---
# 2. Interacting with the DE10-Nano


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
- plug in the mini-usb cable into the UART connector (by the ethernet port)
- the LEDs should light up immediately because it's getting power over the usb cable
  - even if the board is off
- start the UART connection
- most likely USB0, but maybe USB1
```zsh
minicom -D /dev/ttyUSB0 -b 115200
```
- once run, you should see start up of device
- to exit session: press control a, let go of both, press x

---

#### 5.2: SSH Connection
- plug in the micro-usb cable into the board
- connection to the internet is required
- SSH into FPGA
```zsh
ssh nixos@192.168.80.1
```

#### 5.3: SSH Connection with MacBook
- this is done on the MacBook terminal
- get intel linux ip address and username
- Copy SSH key to connect without password
- replace kevmck with your username
- replace that IP address with your linux computer's
```zsh
ssh-copy-id kevmck@141.225.162.254
```
- SSH into intel linx comp
```zsh
ssh kevmck@141.225.162.254
```
- SSH into FPGA from MacBook with jumping
```zsh
ssh nixos@192.168.80.1 -J kevmck@141.225.162.254    
```

---

### 6. Test FPGA wavdump functionality
- on macbook, ssh into fpga with jumping (from 5.3)
- run the wavdump command with -f for fake mics
- run with -r for raw output, not convolved
```zsh
sudo wavdump -f -r fake_mic_test.wav
```
- once a few samples have been generated, press ctl c to stop

- copy the file to macbook for inspection with Audacity
```zsh
scp -J kevmck@141.225.162.254 nixos@192.168.80.1:/home/nixos/fake_mic_test.wav .
```
- from here, changes made to code will need to be rebuilt

---
# 2. Interacting with the DE10-Nano

## Using MacBook to control headless Intel Linux PC

- ssh into the intel linux comp
```zsh
ssh kevmck@141.225.162.254
```
- cd into FPGA folder with nix flake file
```zsh
cd Desktop/phase_array_fossn 
```
- update the changes that were made to the intel linux pc
```zsh
git pull
```
- get inside a nix shell to rebuild any changes
```zsh
# which one should be used???
nix develop 
nix develop --profile profiles/dev
```
- note: if using a dash (nix-develop) nix would expect a default.nix file
  - not using the dash, signifies using a nix.flake file
- for significant changes, it's best use the boot flag
```zsh
nixos-rebuild --target-host nixos@192.168.80.1 --fast --use-remote-sudo --flake .#de10-nano boot -L 
```
- otherwise the switch command is fine
```zsh
nixos-rebuild --target-host nixos@192.168.80.1 --fast --use-remote-sudo --flake .#de10-nano switch -L 
```

## Using Intel Linux PC as main computer
- TODO














