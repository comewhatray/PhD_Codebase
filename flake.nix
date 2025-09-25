{
  description = "PhD_Codebase development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { nixpkgs, ... }:
    let
      system = "aarch64-darwin";
      pkgs = nixpkgs.legacyPackages.;
    in
    {
      devShells..default = pkgs.mkShell {
        buildInputs = with pkgs; [
          python311
          python311Packages.pip
          python311Packages.setuptools
          python311Packages.wheel
          # Add your project dependencies here:
        ];

        shellHook = ''
          echo "🐍 PhD_Codebase development environment loaded!"
          echo "Python version: $(python --version)"
          
          # Create virtual environment if it doesn't exist
          if [ ! -d ".venv" ]; then
            echo "Creating virtual environment..."
            python -m venv .venv
          fi
          
          source .venv/bin/activate
          echo "Virtual environment activated"
        '';
      };
    };
}