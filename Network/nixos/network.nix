
{ config, lib, pkgs, ... }:

{

  networking.hostName = "pi-nix"; # Define your hostname.


  # Easiest to use and most distros use this by default.
  networking.networkmanager.enable = true;


  environment.systemPackages = with pkgs; [
     pkgs.dnsmasq
     pkgs.hostapd
     pkgs.iptables
     pkgs.avahi
     pkgs.nssmdns
     ];


  networking.firewall.enable = false;







}