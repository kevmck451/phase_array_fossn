# Raspberry Pi Access Point Networking Configuration

{ config, lib, pkgs, ... }:

{

  # Set Static IP ----------------------------------------
  networking.firewall.enable = false;
  networking.useDHCP = true;

  networking.interfaces.wlp1s0u1u4.ipv4.addresses = [ {
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
       # just use google. there should be some way to replicate the local system's resolution but couldn't figure
       # it out before we gave up soooo.
       # dnsmasq is advertising itself to dhcp clients of course but also the local system is using it for whatever
       # reason?
       server = [ "8.8.8.8" ];
     };
  };

  networking.dhcpcd.denyInterfaces = [ "wlp1s0u1u4" ];

  # Firewall Configuration --------------------------------
  services.haveged.enable = config.services.hostapd.enable;

  # NAT Fowarding Configuration --------------------------
  systemd.services.custom-nat = {
      description = "Custom NAT setup for wlp1s0u1u4";
      after = [ "network.target" ];
      serviceConfig.ExecStart = ''
        ${pkgs.iptables}/bin/iptables -t nat -A POSTROUTING -o end0 -j MASQUERADE
        ${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o end0 -m state --state RELATED,ESTABLISHED -j ACCEPT
        ${pkgs.iptables}/bin/iptables -A FORWARD -i end0 -o wlp1s0u1u4 -j ACCEPT

        ${pkgs.iptables}/bin/iptables -t nat -A POSTROUTING -o enp1s0u1u2 -j MASQUERADE
        ${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o enp1s0u1u2 -m state --state RELATED,ESTABLISHED -j ACCEPT
        ${pkgs.iptables}/bin/iptables -A FORWARD -i enp1s0u1u2 -o wlp1s0u1u4 -j ACCEPT
      '';
      wantedBy = [ "multi-user.target" ];
    };

        # ${pkgs.iptables}/bin/iptables -t nat -A POSTROUTING -d 192.168.80.0/24 -j ACCEPT
  #      ${pkgs.iptables}/bin/iptables -t nat -A POSTROUTING -o end0 -j MASQUERADE
  #      ${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o end0 -m state --state RELATED,ESTABLISHED -j ACCEPT
  #      ${pkgs.iptables}/bin/iptables -A FORWARD -i end0 -o wlp1s0u1u4 -j ACCEPT
        # ${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o enp1s0u1u2 -m state --state RELATED,ESTABLISHED -j ACCEPT
        # ${pkgs.iptables}/bin/iptables -A FORWARD -i enp1s0u1u2 -o wlp1s0u1u4 -j ACCEPT
        # ${pkgs.iptables}/bin/iptables -A FORWARD -i enp1s0u1u2 -o wlp1s0u1u4 -m state --state RELATED,ESTABLISHED -j ACCEPT
        # ${pkgs.iptables}/bin/iptables -A FORWARD -i wlp1s0u1u4 -o enp1s0u1u2 -j ACCEPT


}