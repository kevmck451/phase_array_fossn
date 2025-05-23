# Raspberry Pi Access Point Networking Configuration

{ config, lib, pkgs, ... }:

{

  # Set Static IP ----------------------------------------
  networking.firewall.enable = false;
  networking.useDHCP = true;

#  networking.bridges.br0 = { interfaces = [ "enp1s0u1u4c2" "enp1s0u1u2" ]; };

  networking.interfaces.enp1s0u1u2.useDHCP = false;
  networking.interfaces.enp1s0u1u4c2.useDHCP = false;

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
     channel = 6; # 6
     networks.wlp1s0u1u4 = {
       ssid = "Phased_Array";
       authentication.mode = "none";
     };
     settings.hw_mode = "g";
  };

  # increase bandwidth for better transfer
#  services.hostapd.radios.wlp1s0u1u4.wifi5.enable = true;
#  services.hostapd.radios.wlp1s0u1u4.wifi5.require = true;
#  services.hostapd.radios.wlp1s0u1u4.wifi5.operatingChannelWidth = "80";

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

  systemd.services.dnsmasq = {
    after = [ "network.target" "sys-subsystem-net-devices-br0.device" ];
    requires = [ "sys-subsystem-net-devices-br0.device" ];
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
  
#  systemd.services.br0-netdev.serviceConfig = #[ "br0-netdev.service" ];

  systemd.services.br0-netdev = {
    serviceConfig = {
      ExecStartPre = "${pkgs.coreutils}/bin/sleep 3";
    };
  };

  systemd.services.br0-recover = {
    description = "Recreate br0 when USB interfaces appear";
    wantedBy = [ "sys-subsystem-net-devices-enp1s0u1u2.device" ];
    after = [ "sys-subsystem-net-devices-enp1s0u1u2.device" ];
    serviceConfig = {
      Type = "oneshot";
      ExecStart = pkgs.writeShellScript "create-br0" ''
        ${pkgs.iproute2}/bin/ip link add name br0 type bridge || true
        ${pkgs.iproute2}/bin/ip link set enp1s0u1u2 master br0 || true
        ${pkgs.iproute2}/bin/ip link set enp1s0u1u4c2 master br0 || true
        ${pkgs.iproute2}/bin/ip addr add 192.168.1.1/24 dev br0 || true
        ${pkgs.iproute2}/bin/ip link set br0 up || true
      '';
    };
  };


}
