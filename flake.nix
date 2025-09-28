{
  description = "A sample flake for Eightfold Finals";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

outputs = { self, nixpkgs, flake-utils, ... }:
  flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [];
      };
    in
    {
      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [
          python313Packages.uv
          portaudio
	  qwen-code
       ];
         shellHook = ''
          # Start the virtual environment
          source .venv/bin/activate
          echo -e "\033[1;36mPython:\033[0m $(python --version 2>&1)"
         '';
        };      
    });
}


