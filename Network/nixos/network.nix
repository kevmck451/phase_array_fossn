# Raspberry Pi Access Point Nix Configuration

{ config, lib, pkgs, ... }:

{

  # Set Static IP ----------------------------------------
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
            address = "192.168.1.143";
            prefixLength = 24;
        }];
    };
  };


  # Packages -------------------------------------------
  environment.systemPackages = with pkgs; [
     hostapd
     dnsmasq
     bridge-utils
  ];


  # Wireless Service ------------------------------------
  hardware.enableRedistributableFirmware = true;
  networking.wireless.enable = true;


  # Wireless Network Configuration ----------------------
  networking.wireless.networks = {
    "KM 5" = {
      psk = "m2d2jkl9123";
    };
  };


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
       interface = [ "br0" ];
       dhcp-range = [
         "br0,192.168.1.100,192.168.1.200,255.255.255.0,12h"
       ];
     };
  };


  # Firewall Configuration --------------------------------
  services.haveged.enable = config.services.hostapd.enable;


  # Bridge configuration -----------------------------------
  networking.bridges.br0.interfaces = [ "end0" "wlp1s0u1u4" ];


  # Set static IP for wlan0 on a different subnet
  networking.interfaces.wlan0.ipv4.addresses = [{
    address = "192.168.2.1";
    prefixLength = 24;
  }];

  # Enable IP forwarding globally
  networking.ipv4.forwarding = true;

# Enable the firewall and configure NAT
  networking.firewall = {
    enable = true;

    # Combine all trusted interfaces here
    trustedInterfaces = [ "br0" "wlan0" "wlp1s0u1u4" ];

    # Allow specific forwarding rules as needed
    allowedUDPPorts = [ 53 67 ]; # Example: allow DNS and DHCP
    allowedTCPPorts = [ 22 ];    # Example: allow SSH
  };

  # NAT configuration to allow wlan0 to access br0 (and beyond)
  networking.nat = {
    enable = true;
    externalInterface = "br0"; # Interface connected to the internet (outgoing)
    internalInterfaces = [ "wlan0" ]; # Interface that should use NAT
  };




}