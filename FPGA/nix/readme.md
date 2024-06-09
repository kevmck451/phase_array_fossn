# Setup for DE10

The initial setup for the DE10 Nano board cannot be setup with anything other than intel processor running linux

The development environment for this project was setup on a [Wo-We Mini PC](https://www.amazon.com/dp/B0CLD8JRWK?psc=1&ref=ppx_yo2ov_dt_b_product_details)
   - Processor: Intel Celeron N4020 CPU @ 1.1GHz x 2 running Ubuntu 20.04.6 64 bit

#### Installing Nix 
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

#### Download Repo from Github
   - de10_nano_nixos_demo from github
     - git@github.com:tpwrules/de10_nano_nixos_demo.git
   - papa_fpga repo
     - git@github.com:tpwrules/papa_fpga.git

cd into folder

#### Build SD Card Image for DE10
this can only be performed on an intel processor with nix installed
this only needs to be done once
then updates can be run from the device itself

run the command:
```zsh
nix build .#nixosConfigurations.de10-nano
```

this will take some time

##### troubleshooting
   - didnt work for me the first time
   - failed with exit code 10 & computer gave low space warning
   - try on intel windows computer using WSL


#### Create Bootable Drive
this can be done on any computer

the build command will make a folder called "result"

inside that folder is sd-image folder
inside that is a .img.zst file

use etcher to put that onto the SD card (you can also use zstdcat/dd)

insert sd card into de10
set de10 mel switches to all 0 (up)
connect to the de10 through the UART mini usb connector







## Project Setup with Nix


1. Start git repo folder
2. Initialize basic Nix files
    - Set up the basic nix folder structure
        - nix/overlay.nix
        - nix/shell.nix
        - flake.nix
    - flake.nix
        - Flakes are experimental feature in Nix that provide a more reproducible and standardized way to manage Nix projects
        - flake.nix is the entry point for defining a flake
        - defines the dependencies, outputs, and other configurations for your project
        - Flakes can make it easier to share and reproduce your Nix configurations
        - pleaseKeepMyInputs: when running garbage collection, nix will delete inputs so if not connected to internet, you wont be able to redownload needed dependencies
    - shell.nix
        - file defines a development environment that can be instantiated with nix-shell
        - It specifies the dependencies and environment setup needed for your project
        - running ‘nix-shell’ enters an environment where all the specified dependencies are available
    - overlay.nix
        - file allows you to define custom package overlays
        - Overlays are a way to extend or modify the set of available Nix packages
        - to add, modify, or override existing packages without changing the upstream Nixpkgs repo
    - Initial folder structure
        - flake.nix file is inside FPGA developmental folder
        - nix folder inside that for all nix files like shell definition and overlays
        - commit files to git or get dirty warning
        - inside FPGA folder, run ‘nix develop’ to start environment
        - a flake.lock file will be auto generated after running this command
        - commit flake.lock file and run again to start development environment
3. Add Quartus-Prime to Nix Packages
4. Setting up the files required for the FPGA design: Terasic System Builder
5. Adding Qsys

setting up nix so that when quartus is used to generate the files needed to program the fpga
it knows what to do with those files and has the correct structures and packages installed

setting up the HPS operating system to include the quartus packages needed to connect the HPS to FPGA fabric
first objective is being able to load a program on the FPGA
   - to do this, the HPS needs to connect to it using the AXI Bridge
     - AXI is protocol used to connect different components like 
       - processors, memory controller, peripherals, and custom logic implemented in the FPGA


Nix defaults and overlays: are you adding terminal command and routing them to specific run commands?



## Building SD Image for DE10 Nano NixOS
once your development environment is functional and you can load a program onto the FPGA
build the NixOS sdImage file which will be in charge of operating the HPS system and
controlling the FPGA


readme.md in papa_fpga to add nixos to de10. how to connect and set up dev environment for running commands



















