{ config, lib, pkgs, ... }:

{

  # uncomplicate using the server
  networking.firewall.enable = false;

  # ethernet interface used with other devices so static ip with no DHCP
  networking.interfaces.eth0.ipv4.addresses = [{
    address = "192.168.0.1";
    prefixLength = 24;
  }];


  # run DHCP for access over USB ethernet gadget
  services.dnsmasq = {
    enable = true;

    settings = {
      bind-interfaces = true;
      interface = [ "eth0" ];
      dhcp-range = [ "192.168.0.100,192.168.0.200,255.255.255.0,12h" ];
    };
  };


  networking.dhcpcd.denyInterfaces = [ "eth0" ];

  networking.wireless.enable = false;




}