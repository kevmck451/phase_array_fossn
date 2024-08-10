
{ config, lib, pkgs, ... }:

{

  networking.hostName = "pi-nix";
  networking.domain = "phased.array";


  # Enable Networking
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