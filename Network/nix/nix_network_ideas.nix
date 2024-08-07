{ config, pkgs, ... }:

{

  services.openssh.enable = true;

  networking = {
    hostName = "pinix";
    useDHCP = false;
    interfaces = {
      eth0 = {
        useDHCP = true;
      };
      wlan0 = {
        useDHCP = true;
        wpa_supplicant = {
          enable = true;
          extraConfig = ''
            network={
              ssid="KM 5"
              psk="m2d2jkl9123"
            }
          '';
        };
      };
      wlan1 = {
        enable = true;
        hostapd = {
          interface = "wlan1";
          ssid = "Phased_Array";
          channel = 1;
          hw_mode = "g";
          driver = "nl80211";
          auth_algs = 1;
          wpa = 0;
        };
      };
      usb0 = {
        enable = true;
        addresses = [ "192.168.80.2/24" ];
      };
    };
    defaultGateway = "192.168.80.1";
  };

  services = {
    hostapd = {
      enable = true;
      interfaces = ["wlan1"];
      ssid = "Phased_Array";
      openNetwork = true;
    };

    dhcpd4 = {
      enable = true;
      interfaces = ["wlan1"];
      extraConfig = ''
        subnet 192.168.80.0 netmask 255.255.255.0 {
          range 192.168.80.10 192.168.80.50;
          option routers 192.168.80.2;
          option domain-name-servers 8.8.8.8, 8.8.4.4;
        }
      '';
    };

    firewall = {
      enable = true;
      interfaces = {
        "eth0" = {
          allowedTCPPorts = [];
          allowedUDPPorts = [];
        };
        "wlan1" = {
          allowedTCPPorts = [];
          allowedUDPPorts = [];
        };
        "usb0" = {
          allowedTCPPorts = [];
          allowedUDPPorts = [];
        };
      };
      extraCommands = ''
        iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
        iptables -A FORWARD -i eth0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT
        iptables -A FORWARD -i wlan1 -o eth0 -j ACCEPT
        iptables -A FORWARD -i eth0 -o usb0 -m state --state RELATED,ESTABLISHED -j ACCEPT
        iptables -A FORWARD -i usb0 -o eth0 -j ACCEPT
        iptables -A FORWARD -i wlan1 -o usb0 -j ACCEPT
        iptables -A FORWARD -i usb0 -o wlan1 -j ACCEPT
      '';
    };
  };

  networking.nat.enable = true;
  networking.nat.externalInterface = "eth0";
  networking.nat.internalInterfaces = ["wlan1" "usb0"];
  networking.nat.enableIPv4Forwarding = true;
}
