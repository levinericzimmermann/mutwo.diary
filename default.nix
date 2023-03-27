{ sources ? import ./nix/sources.nix}:
let
  mutwo-diary = import (sources.mutwo-nix.outPath + "/mutwo.diary/default.nix") {};
  mutwo-diary-local = mutwo-diary.overrideAttrs (
    finalAttrs: previousAttrs: {
       src = ./.;
    }
  );
in
  mutwo-diary-local
