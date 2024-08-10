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
            address = "192.168.0.143";
            prefixLength = 24;
        }];
        wlan0.useDHCP = true;
        wlp1s0u1u4.useDHCP = false;
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
         "br0,192.168.81.100,192.168.81.200,255.255.255.0,12h"
       ];
     };
  };


  # Firewall Configuration --------------------------------
  networking.firewall.allowedUDPPorts = lib.optionals config.services.hostapd.enable [53 67 68]; # DHCP
  networking.firewall.allowedTCPPorts = lib.optionals config.services.hostapd.enable [22]; # ssh
  services.haveged.enable = config.services.hostapd.enable;


  # Bridge configuration -----------------------------------
  networking.bridges.br0.interfaces = [ "end0" "wlp1s0u1u4" ];

  # todo: add NAT for wireless connection to AP
  sysctl."net.ipv4.ip_forward" = true;

  # Ensure these iptables rules are applied on boot
  systemd.services.iptables = {
  description = "Load iptables rules";
  after = [ "network.target" ];
  serviceConfig = {
    ExecStart = "${pkgs.iptables}/bin/iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE";
    ExecStart += "${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o wlan0 -j ACCEPT";
    ExecStart += "${pkgs.iptables}/bin/iptables -A FORWARD -i wlan0 -o wlp1s0u1u4 -m state --state RELATED,ESTABLISHED -j ACCEPT";
    Type = "oneshot";
    RemainAfterExit = true;
  };


}