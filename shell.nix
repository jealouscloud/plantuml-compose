{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/6201e203d09599479a3b3450ed24fa81537ebc4e.tar.gz") {} }:  
pkgs.mkShell {
  buildInputs = [
    pkgs.plantuml
    pkgs.playwright-mcp
  ];
}
