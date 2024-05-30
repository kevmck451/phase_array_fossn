{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: let
    inputs = { inherit nixpkgs; };
    systems = ["x86_64-linux" "aarch64-linux" "aarch64-darwin" ];

    genAttrs = names: f:
      builtins.listToAttrs (
          builtins.map (x: { name = x; value = f x; }) names
      );

    packageFunc = system: let
      pkgs = import nixpkgs {
        inherit system;

        overlays = [
          (final: prev: {
            pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
              (python-final: python-prev: {
                # upgrade to latest version
                amaranth = (python-prev.amaranth.overrideAttrs (o: {
                  version = "0.4.1"; # unstable-2024-01-22

                  src = final.fetchFromGitHub {
                    owner = "amaranth-lang";
                    repo = "amaranth";
                    rev = "b3639c4cc5938148bbd114aa9efbd410d2893824";
                    hash = "sha256-zq7r53UUQ3kAXbiTm5ZHWG+xtjEBg07oiuQeZ9UG4Ds=";
                  };
                }));

                amaranth-boards = (python-prev.amaranth-boards.overrideAttrs (o: {
                  version = "unstable-2023-12-13";

                  src = final.fetchFromGitHub {
                    owner = "amaranth-lang";
                    repo = "amaranth-boards";
                    rev = "170675812b71ee722bcf8ccdb88409a9ad97ffe2";
                    hash = "sha256-9ZyzD4hOGW2sG24ISNwYBY6NiDe5q0rwDeMdYtzjwDA=";
                  };
                }));
              })
            ];
          })
        ];
      };
    in pkgs;

    shellFunc = system: let
      pkgs = packageFunc system;

      # a text file containing the paths to the flake inputs in order to stop
      # them from being garbage collected
      pleaseKeepMyInputs = pkgs.writeTextDir "bin/.please-keep-my-inputs"
        (builtins.concatStringsSep " " (builtins.attrValues inputs));
    in pkgs.mkShell {
      buildInputs = [
        (pkgs.python3.withPackages (p: with p; [
          amaranth
          amaranth-boards
        ]))

        pkgs.yosys
        pkgs.nextpnr
        pkgs.icestorm

        pleaseKeepMyInputs
      ];
    };
  in {
    devShell = genAttrs systems shellFunc;
  };
}
