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
    nat.enable = true;
    firewall.enable = false;
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


# Enable the firewall and configure NAT
#  networking.firewall = {
#    enable = true;
#
#    # Combine all trusted interfaces here
#    trustedInterfaces = [ "br0" "wlan0" "wlp1s0u1u4" ];
#
#    # Allow specific forwarding rules as needed
#    allowedUDPPorts = [ 53 67 ]; # Example: allow DNS and DHCP
#    allowedTCPPorts = [ 22 ];    # Example: allow SSH
#  };

systemd.services.custom-nat = {
  description = "Custom NAT setup for wlp1s0u1u4";
  after = [ "network.target" ];
  serviceConfig.ExecStart = ''
    ${pkgs.iptables}/bin/iptables -t nat -A POSTROUTING -o end0 -j MASQUERADE
    ${pkgs.iptables}/bin/iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
    ${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o end0 -m state --state RELATED,ESTABLISHED -j ACCEPT
    ${pkgs.iptables}/bin/iptables -A FORWARD -i end0 -o wlp1s0u1u4 -j ACCEPT
    ${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
    ${pkgs.iptables}/bin/iptables -A FORWARD -i wlan0 -o wlp1s0u1u4 -j ACCEPT
  '';
  wantedBy = [ "multi-user.target" ];
};




}