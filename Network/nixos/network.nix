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

  services.hostapd = {
    enable = true;
    radios = {
      wlp1s0u1u4 = {
        band = "g"; # Equivalent to hwMode = "g"
        networks = {
          network1 = {
            ssid = "Phased_Array";
            authentication = {
              wpaPassword = "123456789";
            };
          };
        };
      };
    };
  };

  # set up wireless DNS
  services.dnsmasq = lib.optionalAttrs config.services.hostapd.enable {
    enable = true;
    extraConfig = ''
      interface=wlp1s0u1u4
      bind-interfaces
      dhcp-range=10.0.0.10,10.0.0.254,24h
    '';
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
