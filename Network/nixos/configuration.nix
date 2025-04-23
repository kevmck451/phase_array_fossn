
# Raspberry Pi NixOS Configuration

{ config, lib, pkgs, ... }:

{
  imports =
    [
      ./hardware-configuration.nix
      ./network.nix
      ./temp_sensor.nix
    ];

  # BOOTLOADER, rpis always basically need extlinux compatible
  boot.loader.grub.enable = false;
  boot.loader.generic-extlinux-compatible.enable = true;

  boot.kernelModules = [ "8021q" ];
  boot.kernel.sysctl = {
    "net.ipv4.conf.all.forwarding" = true;
  };

  networking.hostName = "pi-nix";

  swapDevices = [ { device = "/swapfile"; size = 1024; } ];

  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  environment.systemPackages = with pkgs; [
    pkgs.nano
    pkgs.git
    pkgs.tmux
    pkgs.htop
    wormhole-william
  ];

  # Set your time zone.
  time.timeZone = "America/Chicago";

  users.mutableUsers = false; # get password etc from configuration file
  users.users.admin = {
    isNormalUser = true;
    extraGroups = [ "wheel" "i2c" ]; # Enable ‘sudo’ for the user.
    # empty password
    hashedPassword = "$6$QgXrKw0FqewNXb$NzqM6h5vtDrTykUKShy/ZgG/zr.sotnRugnrXjRe6Q98Sr8rOmPTEdxPVlHmThEmMePHg9t18ge5yPFsOzGJN/";
    # of KevMcK@MacBook-Pro
    openssh.authorizedKeys.keys = [ "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIObSliOBCGrWo+1YOA3z9l9+XCsWdqQ7MLhB/q2DDCTc KevMcK@MacBook-Pro.local" ];
    packages = with pkgs; [

    ];
  };

  # disable password for sudo
  security.sudo.wheelNeedsPassword = false;
  nixpkgs.config.allowUnfree = true;

  # Configure Keymap in X11
  services.xserver = {
    layout = "us";
    xkbVariant = "";
  };

  # Enable the OpenSSH daemon.
  services.openssh.enable = true;
  services.openssh.settings.PasswordAuthentication = false;
  services.openssh.settings.PermitRootLogin = "no";

  programs.nix-ld.enable = true;

  # For more information, see `man configuration.nix` or https://nixos.org/manual/nixos/stable/options#opt-system.state>
  system.stateVersion = "23.11"; # Did you read the comment?

  # for nixpkgs 205fd4226592

  systemd.services.fpgatunnel = {
    description = "Forward port 7654 to FPGA at 192.168.1.201:2048";
    wantedBy = [ "multi-user.target" ];
    after = [ "network-online.target" ];
    serviceConfig = {
      ExecStart = [
        "${pkgs.openssh}/bin/ssh"
        "-N"
        "-o"
        "StrictHostKeyChecking=no"
        "-o"
        "UserKnownHostsFile=/dev/null"
        "-L"
        "7654:192.168.1.201:2048"
        "admin@localhost"
      ];
      Restart = "always";
    };
  };

}
