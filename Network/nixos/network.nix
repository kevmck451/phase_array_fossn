{ config, lib, pkgs, ... }:

{

  # Set Static IP
  networking = {
    defaultGateway = {
        address = "192.168.0.1";
        interface = "br0";
    };
    nameservers = [ "192.168.0.1" ];
    domain = "local";
    search = [ "pi-nix" ];
    hostName = "pi-nix";
    interfaces = {
        br0.ipv4.addresses = [{
            address = "192.168.0.143";
            prefixLength = 24;
        }];
    };
  };

  # Packages
  environment.systemPackages = with pkgs; [
     hostapd
     dnsmasq
     bridge-utils
  ];

  # Wireless Service
  hardware.enableRedistributableFirmware = true;
  networking.wireless.enable = true;

  # Wireless network connection for wlan0
  networking.wireless.networks = {
    wlan0 = {
      ssid = "KM 5";
      psk = "m2d2jkl9123";  # Use your actual Wi-Fi password
      ipv4 = {
        addresses = [{
          address = "192.168.0.200"; # Set this according to your network
          prefixLength = 24;
        }];
        gateway = "192.168.0.1"; # Your Wi-Fi router IP
      };
    };
  };

   # Wireless Access Point
   networking.networkmanager.unmanaged = [ "Phased_Array:wlp1s0u1u4" ];

   services.hostapd.enable = true;
   services.hostapd.radios.wlp1s0u1u4 = {
     channel = 6;
     networks.wlp1s0u1u4 = {
       ssid = "Phased_Array";
       authentication.mode = "none";
     };
     settings.hw_mode = "g";
   };

  # DNS Configuration
  services.dnsmasq = lib.optionalAttrs config.services.hostapd.enable {
    enable = true;
    settings = {
       bind-interfaces = true;
       interface = [ "br0" ];
       dhcp-range = [
         "br0,192.168.81.100,192.168.81.200,255.255.255.0,12h"
       ];
     };
  };

  networking.firewall.allowedUDPPorts = lib.optionals config.services.hostapd.enable [53 67];
  services.haveged.enable = config.services.hostapd.enable;

  # Bridge configuration
  networking.bridges.br0.interfaces = [ "end0" "wlp1s0u1u4" ];





}