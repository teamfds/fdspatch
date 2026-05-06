{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    pkg-config
    cargo
    rustc
    python311 # Substitua por python315 quando disponível ou python3 para a mais recente
  ];

  buildInputs = with pkgs; [
    fuse
    # openssl
  ];

  # shellHook = ''
  #   export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
  # '';
}
