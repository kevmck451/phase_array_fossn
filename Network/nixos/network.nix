{ config, lib, pkgs, ... }:

{

  # packages
  environment.systemPackages = with pkgs; [
     hostapd
     dnsmasq
     bridge-utils
  ];

  # add wireless service
  hardware.enableRedistributableFirmware = true;
  networking.wireless.enable = true;

  # set up wireless access point
  networking.networkmanager.unmanaged = [ "Phased_Array:wlp1s0u1u4" ];

   # Host APD Setup
   services.hostapd.enable = true;
   services.hostapd.radios.wlp1s0u1u4 = {
     channel = 6;
     networks.wlp1s0u1u4 = {
       ssid = "Phased_Array";
       authentication.mode = "none";
     };
     settings.hw_mode = "g";
   };

  # set up wireless DNS
  services.dnsmasq = lib.optionalAttrs config.services.hostapd.enable {
    enable = true;
    settings = {
       bind-interfaces = true;
       interface = [ "wlp1s0u1u3" "wlan0"]; # "usb0"
       dhcp-range = [
#         "usb0,192.168.80.100,192.168.80.200,255.255.255.0,12h"
         "wlp1s0u1u4,192.168.81.100,192.168.81.200,255.255.255.0,12h"
         "wlan0,192.168.82.100,192.168.82.200,255.255.255.0,12h"
       ];
     };
  };

  networking.firewall.allowedUDPPorts = lib.optionals config.services.hostapd.enable [53 67];
  services.haveged.enable = config.services.hostapd.enable;

  # Bridge configuration
  networking.bridges.br0.interfaces = [ "end0" "wlp1s0u1u4" ];

  # Set Static IP for VLANs (not for bridged interfaces)
  networking.interfaces = {
    vlan2.ipv4.addresses = [{
      address = "192.168.2.1";
      prefixLength = 24;
    }];
    vlan3.ipv4.addresses = [{
      address = "192.168.3.1";
      prefixLength = 24;
    }];
  };

  # Default gateway and nameserver configuration
  networking.defaultGateway = {
    address = "192.168.0.1";
    interface = "end0";
  };
  networking.nameservers = [ "192.168.0.1" ];
  networking.domain = "pi-nix";
  networking.search = [ "pi-nix" ];

  # Virtual LANs configuration
  networking.vlans = {
    vlan2 = {
      id = 2;
      interface = "end0";
    };
    vlan3 = {
      id = 3;
      interface = "end0";
    };
  };

}
