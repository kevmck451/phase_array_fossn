# Raspberry Pi Access Point Networking Configuration

{ config, lib, pkgs, ... }:

{

  # Set Static IP ----------------------------------------
  networking.firewall.enable = false;
  networking.useDHCP = true;

  networking.bridges.br0 = { interfaces = [ "wlp1s0u1u4" "enp1s0u1u2" ]; };

  networking.interfaces.br0.ipv4.addresses = [ {
    address = "192.168.1.1";
    prefixLength = 24;
  } ];

  # Packages -------------------------------------------
  environment.systemPackages = with pkgs; [
     hostapd
     dnsmasq
  ];

  # Wireless Service ------------------------------------
  hardware.enableRedistributableFirmware = true;
  networking.wireless.enable = true;

  # Wireless Access Point --------------------------------
  services.hostapd.enable = true;
  services.hostapd.radios.wlp1s0u1u4 = {
     channel = 40; # 6
     networks.wlp1s0u1u4 = {
       ssid = "Phased_Array";
       authentication.mode = "none";
     };
#     settings.hw_mode = "g";
  };

  # increase bandwidth for better transfer
  services.hostapd.radios.wlp1s0u1u4.wifi5.enable = true;
  services.hostapd.radios.wlp1s0u1u4.wifi5.require = true;
  services.hostapd.radios.wlp1s0u1u4.wifi5.operatingChannelWidth = 80;

  # DNS Configuration -------------------------------------
  services.dnsmasq = lib.optionalAttrs config.services.hostapd.enable {
    enable = true;
    settings = {
       bind-interfaces = true;
       interface = [ "br0" ];
       dhcp-range = [
         "br0,192.168.1.100,192.168.1.200,255.255.255.0,12h"
       ];
       # just use google. there should be some way to replicate the local system's resolution but couldn't figure
       # it out before we gave up soooo.
       # dnsmasq is advertising itself to dhcp clients of course but also the local system is using it for whatever
       # reason?
       server = [ "8.8.8.8" ];
     };
  };

  networking.dhcpcd.denyInterfaces = [ "br0" ];

  # Firewall Configuration --------------------------------
  services.haveged.enable = config.services.hostapd.enable;

  # NAT Fowarding Configuration --------------------------
  systemd.services.custom-nat = {
      description = "Custom NAT setup for wlp1s0u1u4";
      after = [ "network.target" ];
      serviceConfig.ExecStart = ''
        ${pkgs.iptables}/bin/iptables -t nat -A POSTROUTING -o end0 -j MASQUERADE
        ${pkgs.iptables}/bin/iptables -A FORWARD -i br0 o end0 -m state --state RELATED,ESTABLISHED -j ACCEPT
        ${pkgs.iptables}/bin/iptables -A FORWARD -i end0 -o br0 -j ACCEPT
      '';
      wantedBy = [ "multi-user.target" ];
    };
  
  systemd.services.br0-netdev.serviceConfig = #[ "br0-netdev.service" ];

  { 
  ExecStartPre = "${pkgs.coreutils}/bin/sleep 3"; # until i guess the wifi or usb or whichever comes up??? 1 was sufficient but better safe
  };


}
