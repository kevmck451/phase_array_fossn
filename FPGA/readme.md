# __Setup Instructions for DE10-Nano__
- Building the necessary libraries for DE10 Nano board must be done with:
  - a pc with an intel processor running linux (ubuntu used in this)
  - around 35GB of space for the nix store
- The development environment for this project was setup on a [Wo-We Mini PC](https://www.amazon.com/dp/B0CLD8JRWK?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- Processor used for this: Intel Celeron N4020 CPU @ 1.1GHz x 2 running Ubuntu 20.04.6 64 bit

---

### __1. Installing Nix__
   - [Nix Website](https://nixos.org/download/#nixos-iso)
   - Browsing for Nix Packages [Package Search Website](https://search.nixos.org/packages?ref=itsfoss.com)

Adding the flake feature in ubuntu
```zsh
sudo nano /etc/nix/nix.conf
```
Add this to the config file
~~~
experimental-features = nix-command flakes
~~~

---

### 2. Download Repo from Github
- These are the two already built systems for the DE10
- First attempt will be done with 1

1. de10_nano_nixos_demo from github
   - git@github.com:tpwrules/de10_nano_nixos_demo.git
2. papa_fpga repo
   - git@github.com:tpwrules/papa_fpga.git

cd into folder

---

### 3. Build SD Card Image for DE10
- this can only be performed on an intel processor with nix installed
- this only needs to be done once
- then updates can be run from the device itself

- run the command:
```zsh
nix build .#nixosConfigurations.de10-nano
```

- this will take some time

##### troubleshooting
   - didnt work for me the first time
   - failed with exit code 10 & computer gave low space warning
   - tried build command again and it worked

---

### 4. Create Bootable Drive
- this can be done on any computer

- the build command will make a folder called "result"

- inside that folder is sd-image folder
- inside that is a .img.zst file

- use etcher to put that onto the SD card 
- you can also use zstdcat/dd
   - this decompresses the image and writes it to the SD card

#### zstdcat/dd terminal method
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

- from here there are several ways to connect to the DE10
    - it will depend on exactly how the NixOS was designed
    - creating a putty terminal and connecting over UART will be the simplest
    
#### PuTTY on Ubuntu
```zsh
sudo apt install putty
```
- start the putty application from terminal or app
```zsh
putty
```
#### UART PuTTY Configuration
~~~
Connection Type: Serial
Serial Line: /dev/ttyUSB0
Speed: 115200
~~~

- finding the UART connection destination for the Serial Line 











