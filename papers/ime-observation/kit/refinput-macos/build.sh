#!/usr/bin/env bash
# Build the macOS reference input field into .build/refinput-macos (the directory is ignored by git).
set -eu
cd "$(dirname "$0")"
if ! command -v swiftc >/dev/null 2>&1; then
  echo "build.sh: swiftc not found (install the Xcode command line tools)" >&2
  exit 2
fi
mkdir -p .build
swiftc -O RefInput.swift -o .build/refinput-macos
echo "built: $(pwd)/.build/refinput-macos"
