{ lib
, buildPythonPackage
, fetchFromGitHub
, pytz
, smbus2
}:

buildPythonPackage rec {
  pname = "bme280";
  version = "0.2.4";

  src = fetchFromGitHub {
    owner = "rm-hull";
    repo = "bme280";
    rev = "${version}";
    sha256 = "sha256-sw/bkTdrnPhBhrnk5yyXCbEK4kMo+PdEvoMJ9aaZbsE=";
  };

  propagatedBuildInputs = [ cython ];

  # doCheck = false;

  meta = with lib; {
#    homepage = "https://github.com/swistakm/pyimgui";
#    description = "Python bindings for the amazing dear imgui C++ library - a Bloat-free Immediate Mode Graphical User Interface.";
#    license = licenses.bsd3;
#    platforms = platforms.linux;
  };
}