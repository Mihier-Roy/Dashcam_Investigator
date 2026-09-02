{
  description = "Dashcam Investigator dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python312
            pkgs.uv
            pkgs.exiftool
          ];

          # PySide6/QtWebEngine ships its own Qt/Chromium libs via the
          # uv-managed venv; give them the system libs they dlopen at
          # runtime (Chromium's usual desktop-integration dependency set).
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.libGL
            pkgs.fontconfig
            pkgs.freetype
            pkgs.glib
            pkgs.gtk3
            pkgs.atk
            pkgs.at-spi2-atk
            pkgs.at-spi2-core
            pkgs.cairo
            pkgs.pango
            pkgs.gdk-pixbuf
            pkgs.cups
            pkgs.dbus
            pkgs.expat
            pkgs.libdrm
            pkgs.mesa
            pkgs.libgbm
            pkgs.alsa-lib
            pkgs.libpulseaudio
            pkgs.libxcb-cursor
            pkgs.libxcb-wm
            pkgs.libxcb-util
            pkgs.libxcb-image
            pkgs.libxcb-keysyms
            pkgs.libxcb-render-util
            pkgs.zlib
            pkgs.systemdLibs
            pkgs.zstd
            pkgs.brotli
            pkgs.nss
            pkgs.nspr
            pkgs.krb5
            pkgs.libxkbcommon
            pkgs.libxkbfile
            pkgs.libx11
            pkgs.libxext
            pkgs.libxcb
            pkgs.libxcomposite
            pkgs.libxdamage
            pkgs.libxfixes
            pkgs.libxrandr
            pkgs.libxtst
            pkgs.libxrender
            pkgs.libxi
            pkgs.libxcursor
            pkgs.libxscrnsaver
            pkgs.libxshmfence
            pkgs.libxinerama
          ];

          shellHook = ''
            export UV_PYTHON=${pkgs.python312}/bin/python3.12
            # Not NixOS: no /run/opengl-driver symlink, so point Mesa at
            # the store driver directly instead of falling back to
            # software rasterization via a broken GBM DRI lookup.
            export LIBGL_DRIVERS_PATH=${pkgs.mesa}/lib/dri
            # QtWebEngine's Chromium compositor otherwise loops forever
            # failing to acquire a GPU dma-buf/Vulkan texture and never
            # paints its view; run its content without GPU compositing.
            export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu"
          '';
        };
      });
}
