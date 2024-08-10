
{ config, lib, pkgs, ... }:

{

  # Set Static IP
  networking = {
    defaultGateway = {
        address = "192.168.0.1";
        interface = "end0";
    };
    nameservers = [ "192.168.0.1" ];
    domain = "pi-nix";
    search = [ "pi-nix" ];
    interfaces = {
        end0.ipv4.address = [{
            address = "192.168.0.143";
            prefixLength = 24;
        }];
    };
  };

  # Enable Networking
#  networking.networkmanager.enable = true;
#
#  environment.systemPackages = with pkgs; [
#     pkgs.dnsmasq
#     pkgs.hostapd
#     pkgs.iptables
#     pkgs.avahi
#     pkgs.nssmdns
#     ];
#
#  networking.firewall.enable = false;















}