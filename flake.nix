{
  description = "PhD_Codebase development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { nixpkgs, ... }:
    let
      system = "aarch64-darwin";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          python312
          python312Packages.pip
          # Add your project dependencies here:
	  #python312Packages.numpy
	  #python312Packages.pandas
          #python312Packages.matplotlib
	  #python312Packages.networkx
	  #python312Packages.shapely
	  #python312Packages.scipy
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
