{ config, lib, pkgs, ... }:
{
  networking.firewall.enable = false;

  nixpkgs.config.allowUnfree = true;
  environment.systemPackages = with pkgs; [
        pkgs.openssh
        git
        tmux
        htop
  ];

  services.openssh.enable = true;
}