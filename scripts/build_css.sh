#!/usr/bin/env bash
# Compiles the ui/ module's Tailwind CSS + daisyUI theme using the standalone
# Tailwind CLI (no Node/npm, per ADR 0001). Downloads the CLI binary and the
# daisyUI standalone bundle on first run, caching both in .tailwindcss-cli/
# (gitignored) and integrationsandbox/ui/css_src/ respectively.
set -euo pipefail

TAILWIND_VERSION="v4.3.3"
BIN_DIR=".tailwindcss-cli"
BIN_PATH="$BIN_DIR/tailwindcss"
CSS_SRC_DIR="integrationsandbox/ui/css_src"
DAISYUI_BUNDLE="$CSS_SRC_DIR/daisyui.mjs"
INPUT_CSS="$CSS_SRC_DIR/input.css"
OUTPUT_CSS="integrationsandbox/ui/static/css/output.css"

os="$(uname -s)"
arch="$(uname -m)"

case "$os-$arch" in
  Darwin-arm64) asset="tailwindcss-macos-arm64" ;;
  Darwin-x86_64) asset="tailwindcss-macos-x64" ;;
  Linux-x86_64) asset="tailwindcss-linux-x64" ;;
  Linux-aarch64|Linux-arm64) asset="tailwindcss-linux-arm64" ;;
  *)
    echo "Unsupported platform: $os-$arch" >&2
    exit 1
    ;;
esac

mkdir -p "$BIN_DIR"
if [ ! -x "$BIN_PATH" ]; then
  echo "Downloading Tailwind CLI $TAILWIND_VERSION ($asset)..."
  curl -sL "https://github.com/tailwindlabs/tailwindcss/releases/download/$TAILWIND_VERSION/$asset" -o "$BIN_PATH"
  chmod +x "$BIN_PATH"
fi

if [ ! -f "$DAISYUI_BUNDLE" ]; then
  echo "Downloading daisyUI standalone bundle..."
  curl -sL "https://github.com/saadeghi/daisyui/releases/latest/download/daisyui.mjs" -o "$DAISYUI_BUNDLE"
fi

"$BIN_PATH" -i "$INPUT_CSS" -o "$OUTPUT_CSS" --minify
