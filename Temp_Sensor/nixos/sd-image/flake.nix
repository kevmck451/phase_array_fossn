# https://github.com/jason-m/whydoesnothing.work/blob/main/episode-5/flake.nix

{
  description = "Base system for raspberry pi 4";
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.11";
    nixos-generators = {
      url = "github:nixos-community/nixos-generators";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, nixos-generators, ... }:
  {
    nixosModules = {
      system = {
        disabledModules = [
          "profiles/base.nixos"
        ];

        system.stateVersion = "23.11";
      };
      users = {
        users.users = {
          admin = {
            password = "nixos";
            isNormalUser = true;
            extraGroups = [ "wheel" ];
          };
        };
      };
    };

    packages.aarch64-linux = {
      sdcard = nixos-generators.nixosGenerate {
        system = "aarch64-linux";
        format = "sd-aarch64";
        modules = [
          ./configuration.nix
          self.nixosModules.system
          self.nixosModules.users
        ];
      };
    };
  };
}
