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
    sha256 = "sha256-1Wkzx7b7aNsCc4LhNhuWi5sfXgMeq+MA17lJw+XjxYM=";
  };

  propagatedBuildInputs = [ pytz smbus2 ];

  doCheck = false;

  meta = with lib; {
#    homepage = "https://github.com/swistakm/pyimgui";
#    description = "Python bindings for the amazing dear imgui C++ library - a Bloat-free Immediate Mode Graphical User Interface.";
#    license = licenses.bsd3;
#    platforms = platforms.linux;
  };
}