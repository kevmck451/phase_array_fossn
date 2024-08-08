
# FOSNN Access Point with NixOS on Raspberry Pi 4

{ config, lib, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  # Host APD Setup
#  services.hostapd.enable = true;
#  services.hostapd.radios.wlp1s0u1u3 = {
#    channel = 6;
#    networks.wlp1s0u1u3 = {
#      ssid = "Phased_Array";
#      authentication.mode = "none";
#    };
#
#    settings.hw_mode = "g";
#  };

  # DHCP Server
#  services.dnsmasq = {
#    enable = true;
#
#    settings = {
#      bind-interfaces = true;
#      interface = [ "usb0" "wlp1s0u1u3" "wlan0"];
#      dhcp-range = [
#        "usb0,192.168.80.100,192.168.80.200,255.255.255.0,12h"
#        "wlp1s0u1u3,192.168.81.100,192.168.81.200,255.255.255.0,12h"
#        "wlan0,192.168.82.100,192.168.82.200,255.255.255.0,12h"
#      ];
#    };
#  };

  # Network Interfaces Configuration
#  networking.interfaces = {
#    eth0 = {
#      useDHCP = true;
#    };
#    usb0 = {
#      useDHCP = false;
#      ipv4.addresses = [
#        {
#          address = "192.168.80.1";
#          prefixLength = 24;
#        }
#      ];
#    };
#    wlan0 = {
#      useDHCP = true;
#    };
#    wlp1s0u1u3 = {
#      useDHCP = false;
#    };
#  };
#
#  networking.bridges = {
#    br0.interfaces = [ "eth0" "usb0" "wlan0" "wlp1s0u1u3" ];  # Bridge interfaces together
#  };
#
#  networking.nat = {
#    enable = true;
#    externalInterface = "eth0";  # Assuming eth0 connects to the internet
#    internalInterfaces = [ "br0" ];  # NAT traffic from the bridge
#  };
#
#  networking.defaultGateway = "eth0";  # Set default gateway to Ethernet


  # Use the extlinux boot loader. (NixOS wants to enable GRUB by default)
  boot.loader.grub.enable = false;
  # Enables the generation of /boot/extlinux/extlinux.conf
  boot.loader.generic-extlinux-compatible.enable = true;

  networking.hostName = "pi-nixos"; # Define your hostname.

  # Pick only one of the below networking options.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.
  networking.networkmanager.enable = true;  # Easiest to use and most distros use this by default.

  # Enable mDNS/Bonjour/Avahi
  services.avahi = {
    enable = true;
    nssmdns = true;
  };

  # Set your time zone.
  time.timeZone = "America/Chicago";

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
#   networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Select internationalisation properties.
  # i18n.defaultLocale = "en_US.UTF-8";
  # console = {
  #   font = "Lat2-Terminus16";
  #   keyMap = "us";
  #   useXkbConfig = true; # use xkb.options in tty.
  # };

  # Enable the X11 windowing system.
  # services.xserver.enable = true;

  # Configure keymap in X11
  # services.xserver.xkb.layout = "us";
  # services.xserver.xkb.options = "eurosign:e,caps:escape";

  # Enable CUPS to print documents.
  # services.printing.enable = true;

  # Enable sound.
  # sound.enable = true;
  # hardware.pulseaudio.enable = true;

  # Enable touchpad support (enabled default in most desktopManager).
  # services.xserver.libinput.enable = true;

  # Define a user account. Don't forget to set a password with ‘passwd’.
   users.users.admin = {
     isNormalUser = true;
     extraGroups = [ "wheel" ]; # Enable ‘sudo’ for the user.
     packages = with pkgs; [
  #    firefox
  #     tree
     ];
   };

#  security.pam.services.sshd.allowNullPassword = true;

  # Allow the user to log in as root without a password.
#  users.users.root.initialHashedPassword = "";

  # Allow passwordless sudo from nixos user
#  security.sudo = {
#    enable = true;
#    wheelNeedsPassword = false;
#  };

  # Automatically log in at the virtual consoles.
#  services.getty.autologinUser = "nixos";

  # List packages installed in system profile. To search, run:
  # $ nixos search wget
   environment.systemPackages = with pkgs; [
     pkgs.nano
     pkgs.git
     pkgs.tmux
     pkgs.htop
     pkgs.dnsmasq
     pkgs.hostapd
     pkgs.iptables
     pkgs.avahi
     pkgs.nssmdns
     ];

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  # List services that you want to enable:

  # Enable the OpenSSH daemon.
  services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
   networking.firewall.enable = false;

  # enable flakes and experimental commands
  # and make the root user always trusted
#  nixos.extraOptions = ''
#    experimental-features = nixos-command flakes
#    trusted-users = @wheel
#  '';

  # Copy the NixOS configuration file and link it from the resulting system
  # (/run/current-system/configuration.nixos). This is useful in case you
  # accidentally delete configuration.nixos.
  # system.copySystemConfiguration = true;

  # This option defines the first version of NixOS you have installed on this particular machine,
  # and is used to maintain compatibility with application data (e.g. databases) created on older NixOS versions.
  #
  # Most users should NEVER change this value after the initial install, for any reason,
  # even if you've upgraded your system to a new NixOS release.
  #
  # This value does NOT affect the Nixpkgs version your packages and OS are pulled from,
  # so changing it will NOT upgrade your system.
  #
  # This value being lower than the current NixOS release does NOT mean your system is
  # out of date, out of support, or vulnerable.
  #
  # Do NOT change this value unless you have manually inspected all the changes it would make to your configuration,
  # and migrated your data accordingly.
  #
  # For more information, see `man configuration.nixos` or https://nixos.org/manual/nixos/stable/options#opt-system.state>
  system.stateVersion = "23.11"; # Did you read the comment?

}

