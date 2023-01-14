with import <nixpkgs> {};
with pkgs.python310Packages;


let

  mutwo-clock-archive = builtins.fetchTarball "https://github.com/levinericzimmermann/mutwo.clock/archive/423baf0571b4485066ab82200effab5a38b74c86.tar.gz";
  mutwo-clock = import (mutwo-clock-archive + "/default.nix");

in

  buildPythonPackage rec {
    name = "mutwo.diary";
    src = fetchFromGitHub {
      owner = "levinericzimmermann";
      repo = name;
      rev = "44c402d2cebaee9405e50a01cad1ebb940bd7151";
      sha256 = "sha256-6cZh5K35XNl5unB/Aya/tdixXBoSsafoSd43/PzCRwo=";
    };
    checkInputs = [
      python310Packages.pytest
    ];
    propagatedBuildInputs = [ 
      python310Packages.zodb
      mutwo-clock
      python310Packages.numpy
    ];
    checkPhase = ''
      runHook preCheck
      pytest
      runHook postCheck
    '';
    doCheck = true;
  }
