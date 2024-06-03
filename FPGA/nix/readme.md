# Nix Info

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
        - flake.nix file under outputs: change system to your system
        - commit files to git or get dirty warning
        - inside FPGA folder, run ‘nix develop’ to start environment
        - a flake.lock file will be auto generated after running this command
        - commit flake.lock file and run again to start development environment
