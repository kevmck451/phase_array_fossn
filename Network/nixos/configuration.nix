
# FOSNN Access Point with NixOS on Raspberry Pi 4

{ config, lib, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
      ./network.nix
    ];


#  boot.loader.grub.enable = false;
#  boot.loader.generic-extlinux-compatible.enable = true;

  # BOOTLOADER
  boot.loader.grub.enable = false;
  boot.loader.grub.device = "/dev/sda";
  boot.loader.grub.useOSProber = true;

  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  # Set your time zone.
  time.timeZone = "America/Chicago";

  # Select Internationalistation Properties
  i18n.defaultLocale = "enCA.UTF-8";

  # Define a user account. Don't forget to set a password with ‘passwd’.
   users.users.admin = {
     isNormalUser = true;
     extraGroups = [ "wheel" ]; # Enable ‘sudo’ for the user.
     packages = with pkgs; [

     ];
   };

   users.users.kevmck = {
     isNormalUser = true;
     extraGroups = [ "wheel" ]; # Enable ‘sudo’ for the user.
     packages = with pkgs; [

     ];
   };

  # List packages installed in system profile. To search, run:
  # $ nix search wget
   environment.systemPackages = with pkgs; [
     pkgs.nano
     pkgs.git
     pkgs.tmux
     pkgs.htop
     ];

  # Enable the OpenSSH daemon.
   services.openssh.enable = true;

   # Configure Keymap in X11
   services.xserver = {
     layout = "us";
     xkbVariant = "";
   };

  # For more information, see `man configuration.nix` or https://nixos.org/manual/nixos/stable/options#opt-system.state>
  system.stateVersion = "23.11"; # Did you read the comment?

}
