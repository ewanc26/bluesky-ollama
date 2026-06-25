{
  description = "bluesky-ollama — AI-powered Bluesky bot using Ollama";

  # Pin to nixos-25.11 for stability. Avoids surprises from rolling nixpkgs.
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

  outputs = { self, nixpkgs }:
    let
      # Cover both x86 and ARM on Linux and macOS for local dev and CI.
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      # ── Dev Shell ────────────────────────────────────────────────────────────
      # Minimal shell: just Python 3, pip, and virtualenv.
      # The real dependencies live in requirements.txt.
      devShells = forAllSystems (system:
        let pkgs = nixpkgs.legacyPackages.${system}; in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              python3
              python3Packages.pip
              python3Packages.virtualenv
            ];

            shellHook = ''
              echo "bluesky-ollama dev shell ready (Python 3)"
            '';
          };
        }
      );

      # ── Formatter ────────────────────────────────────────────────────────────
      formatter = forAllSystems (pkgs: pkgs.nixfmt-rfc-style);
    };
}
