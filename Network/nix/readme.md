# Loading and Building Networking NixOS for Raspberry Pi



```zsh
sudo nix build --extra-experimental-features nix-command --extra-experimental-features flakes .#packages.aarch64-linux.sdcard

```