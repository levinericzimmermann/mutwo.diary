let
  sourcesTarball = fetchTarball "https://github.com/mutwo-org/mutwo-nix/archive/refs/heads/main.tar.gz";
  mutwo-diary = import (sourcesTarball + "/mutwo.diary/default.nix") {};
  mutwo-diary-local = mutwo-diary.overrideAttrs (
    finalAttrs: previousAttrs: {
       src = ./.;
    }
  );
in
  mutwo-diary-local
