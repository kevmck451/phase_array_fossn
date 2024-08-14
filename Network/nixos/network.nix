# Raspberry Pi Access Point Nix Configuration

{ config, lib, pkgs, ... }:

{

  # Set Static IP ----------------------------------------
  networking.firewall.enable = false;
  networking.useDHCP = true;

  # Packages -------------------------------------------
  environment.systemPackages = with pkgs; [
     hostapd
     dnsmasq
     bridge-utils
  ];


  # Wireless Service ------------------------------------
  hardware.enableRedistributableFirmware = true;
  networking.wireless.enable = true;




   # Wireless Access Point --------------------------------
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
         "wlp1s0u1u4,192.168.1.100,192.168.1.200,255.255.255.0,12h"
       ];
     };
  };


  # Firewall Configuration --------------------------------
  services.haveged.enable = config.services.hostapd.enable;


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
    # ${pkgs.iptables}/bin/iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
    ${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o end0 -m state --state RELATED,ESTABLISHED -j ACCEPT
    ${pkgs.iptables}/bin/iptables -A FORWARD -i end0 -o wlp1s0u1u4 -j ACCEPT
    # ${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
    # ${pkgs.iptables}/bin/iptables -A FORWARD -i wlan0 -o wlp1s0u1u4 -j ACCEPT
  '';
  wantedBy = [ "multi-user.target" ];
};




}