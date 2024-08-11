

{ config, lib, pkgs, ... }:

{


  # Set Static IP ----------------------------------------
  networking = {
      defaultGateway.address = "192.168.0.1";
      nameservers = [ "192.168.0.1" ];
      domain = "local";
      search = [ "pi-nix" ];
      hostName = "pi-nix";

      interfaces = {
        wlan0 = {
          ipv4.addresses = [{
            address = "192.168.0.200";
            prefixLength = 24;
          }];
          wifi = {
            ssid = "KM 5";
            psk = "m2d2jkl9123";
          };
        };
        end0.ipv4.addresses = [{
          address = "192.168.0.143";
          prefixLength = 24;
        }];
      };
      wireless.enable = true;
  };


  # Packages -------------------------------------------
  environment.systemPackages = with pkgs; [
     hostapd
     dnsmasq
     bridge-utils
  ];



   # Wireless Access Point --------------------------------
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

  # DNS Configuration -------------------------------------
  services.dnsmasq = lib.optionalAttrs config.services.hostapd.enable {
    enable = true;
    settings = {
       bind-interfaces = true;
       interface = [ "wlp1s0u1u4" ];
       dhcp-range = [
         "br0,192.168.0.201,192.168.0.250,255.255.255.0,12h"
       ];
     };
  };


  # Bridge configuration -----------------------------------
  networking.bridges.br0.interfaces = [ "wlan0" "wlp1s0u1u4" ];










}