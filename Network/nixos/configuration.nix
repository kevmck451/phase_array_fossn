
# Raspberry Pi NixOS Configuration

{ config, lib, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
      ./network.nix
    ];

  # BOOTLOADER, rpis always basically need extlinux compatible
  boot.loader.grub.enable = false;
  boot.loader.generic-extlinux-compatible.enable = true;

  boot.kernelModules = [ "8021q" ];
  boot.kernel.sysctl = {
    "net.ipv4.conf.all.forwarding" = true;
  };

  swapDevices = [ { device = "/swapfile"; size = 1024; } ];

  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  environment.systemPackages = with pkgs; [
    pkgs.nano
    pkgs.git
    pkgs.tmux
    pkgs.htop
  ];

  # Set your time zone.
  time.timeZone = "America/Chicago";

  users.mutableUsers = false; # get password etc from configuration file
  users.users.admin = {
    isNormalUser = true;
    extraGroups = [ "wheel" ]; # Enable ‘sudo’ for the user.
    # empty password
    hashedPassword = "$6$QgXrKw0FqewNXb$NzqM6h5vtDrTykUKShy/ZgG/zr.sotnRugnrXjRe6Q98Sr8rOmPTEdxPVlHmThEmMePHg9t18ge5yPFsOzGJN/";
    packages = with pkgs; [

    ];
  };

  # disable password for sudo
  security.sudo.wheelNeedsPassword = false;

  nixpkgs.config.allowUnfree = true;

  # Configure Keymap in X11
  services.xserver = {
    layout = "us";
    xkbVariant = "";
  };

  # Enable the OpenSSH daemon.
  services.openssh.enable = true;
  programs.nix-ld.enable = true;

  # For more information, see `man configuration.nix` or https://nixos.org/manual/nixos/stable/options#opt-system.state>
  system.stateVersion = "23.11"; # Did you read the comment?

}
