
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
  networking.networkmanager.unmanaged = [ "Phased_Array:wlp1s0u1u4" ]
    ++ lib.optional config.services.hostapd.enable "Phased_Array:${config.services.hostapd.interface}";
  services.hostapd = {
    enable = true;
    interface = "wlp1s0u1u4";
    hwMode = "g";
    ssid = "Phased_Array";
    wpaPassphrase = "123456";
  };


  # set up wireless static IP address
  networking.interfaces.wlp1s0u1u4.ip4 = lib.mkOverride 0 [ ];
  networking.interfaces.wlp1s0u1u4.ipv4.addresses =
    lib.optionals config.services.hostapd.enable [{ address = "10.0.0.1"; prefixLength = 24; }];


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

  # Finally, bridge ethernet and wifi
  networking.bridges.br0.interfaces = [ "end0" "wlp1s0u1u4" ];

  # Set Static IP
  networking = {
    defaultGateway = {
        address = "192.168.0.1";
        interface = "end0";
    };
    nameservers = [ "192.168.0.1" ];
    domain = "pi-nix";
    search = [ "pi-nix" ];
    interfaces = {
        end0.ipv4.addresses = [{
            address = "192.168.0.143";
            prefixLength = 24;
        }];
        vlan2.ipv4.addresses = [{
            address = "192.168.2.1";
            prefixLength = 24;
        }];
        vlan3.ipv4.addresses = [{
            address = "192.168.3.1";
            prefixLength = 24;
        }];



    };

    # Virtual LANS
    vlans = {
        vlan2 = {
            id = 2;
            interface = "end0";
        };

        vlan3 = {
            id = 3;
            interface = "end0";
        };

    };

  };















}