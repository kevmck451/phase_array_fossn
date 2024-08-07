# This file is also available under the terms of the MIT license.
# See /LICENSE.mit and /readme.md for more information.
{ stdenvNoCC
, lib
, python3
, yosys
}:

let
  pyEnv = python3.withPackages (p: [
    p.amaranth
    p.amaranth-soc
    p.amaranth-boards
    p.numpy
  ]);

in stdenvNoCC.mkDerivation {
  name = "amaranth_top";

  # TODO: fix source specification
  src = lib.sources.sourceByRegex ./../../../design/amaranth_top [
    "amaranth_top"
    ".*/[^/]*\.py$"
    ".*/[^/]*\.txt$"
  ];

  nativeBuildInputs = [ pyEnv yosys ];

  buildPhase = ''
    runHook preBuild

    mkdir -p $out
    python3 -m amaranth_top.top_fpga $out/build/
    rm -f $out/build/*.bat # will never be executed

    runHook postBuild
  '';
}
