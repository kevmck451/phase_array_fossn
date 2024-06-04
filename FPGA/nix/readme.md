# Nix Info

## Project Setup with Nix

The intial setup for the DE10 Nano board cannot be setup with anything other than intel processor running linux




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



















