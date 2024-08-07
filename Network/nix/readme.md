# Loading and Building Networking NixOS for Raspberry Pi


- install a premade version of nix for pi
- [Tutorial](https://mtlynch.io/nixos-pi4/)

```zsh
sudo nix-channel --update
nix-env -iA nixos.git
```

```zsh
git clone https://github.com/kevmck451/phase_array_fossn.git
```
```zsh
cd phase_array_fossn/Network/nix/pi_sdcard
```
```zsh
sudo nix build --extra-experimental-features nix-command --extra-experimental-features flakes .#packages.aarch64-linux.sdcard
```

```zsh
scp nixos@192.168.0.137:~/phase_array_fossn/Network/nix/pi_sdcard/flake.lock ~/Downloads/
```
```zsh
scp -r nixos@192.168.0.137:~/phase_array_fossn/Network/nix/pi_sdcard/result ~/Downloads/
```
- remove sd card from pi and flash with new sd card image
```zsh

```

```zsh

```

```zsh

```