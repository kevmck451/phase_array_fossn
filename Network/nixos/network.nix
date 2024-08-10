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

  # packages
  environment.systemPackages = with pkgs; [
     hostapd
     dnsmasq
     bridge-utils
  ];

  # add wireless service
  hardware.enableRedistributableFirmware = true;
  networking.wireless.enable = true;

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

  # DNS
  services.dnsmasq = lib.optionalAttrs config.services.hostapd.enable {
    enable = true;
    settings = {
       bind-interfaces = true;
       interface = [ "wlp1s0u1u3"];
       dhcp-range = [
         "wlp1s0u1u4,192.168.81.100,192.168.81.200,255.255.255.0,12h"
       ];
     };
  };

  networking.firewall.allowedUDPPorts = lib.optionals config.services.hostapd.enable [53 67];
  services.haveged.enable = config.services.hostapd.enable;

  # Bridge configuration
  networking.bridges.br0.interfaces = [ "end0" "wlp1s0u1u4" ];





}