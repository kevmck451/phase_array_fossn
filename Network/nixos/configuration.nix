
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

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.admin = {
    isNormalUser = true;
    extraGroups = [ "wheel" ]; # Enable ‘sudo’ for the user.
    packages = with pkgs; [

    ];
  };

  security.sudo.extraRules= [
    { users = [ "admin" ];
      commands = [
        { command = "ALL";
          options = [ "NOPASSWD" ];
        }
      ];
    }
  ];

  nixpkgs.config.allowUnfree = true;

  # Configure Keymap in X11
  services.xserver = {
    layout = "us";
    xkbVariant = "";
  };

  # Enable the OpenSSH daemon.
  services.openssh.enable = true;
  services.qemuGuest.enable = true;
  programs.nix-ld.enable = true;

  # For more information, see `man configuration.nix` or https://nixos.org/manual/nixos/stable/options#opt-system.state>
  system.stateVersion = "23.11"; # Did you read the comment?

}
