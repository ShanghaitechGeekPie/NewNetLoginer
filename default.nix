{
  config,
  dream2nix,
  lib,
  ...
}: {
  imports = [
    dream2nix.modules.dream2nix.WIP-python-pdm
  ];
  deps = {nixpkgs, ...}: {
    python = nixpkgs.python3;
  };
  pdm.lockfile = ./pdm.lock;
  pdm.pyproject = ./pyproject.toml;
  mkDerivation = {
    src = ./.;
    buildInputs = [
      config.deps.python.pkgs.pdm-backend
    ];
  };
}
