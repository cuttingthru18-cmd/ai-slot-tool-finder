#!/bin/bash
# Build AI Slot Tool Finder.app — the menu bar machine.
#
#   ./build.sh            build into ./dist
#   ./build.sh --install  build, then install to /Applications and launch it
#
# No Xcode project, no package manager, no dependencies. One Swift file and the
# command line tools, which is all a menu bar app has ever needed.

set -euo pipefail
cd "$(dirname "$0")"

NAME="AI Slot Tool Finder"
BIN="AISlotToolFinder"
VERSION="1.0.0"
APP="dist/$NAME.app"

command -v swiftc >/dev/null || {
  echo "error: swiftc not found. Install the Xcode command line tools:" >&2
  echo "  xcode-select --install" >&2
  exit 1
}

# The feed ships INSIDE the app as well as being fetched, so a first launch with no
# network still opens to a full shelf instead of an empty machine.
[ -f ../tools.json ] || { echo "error: ../tools.json missing — run 'python3 build_site.py' first" >&2; exit 1; }

# Universal, not just arm64. Half the Macs in the world are still Intel, and an
# arm64-only build fails on them with "application is not supported on this Mac" —
# which reads as a broken app, not an unsupported one.
echo "==> compiling (universal: arm64 + x86_64)"
rm -rf "$APP" dist/.build
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" dist/.build

for arch in arm64 x86_64; do
  swiftc -O \
    -target "$arch-apple-macos13.0" \
    -framework AppKit -framework SwiftUI \
    -o "dist/.build/$BIN-$arch" \
    Sources/main.swift
done

lipo -create -output "$APP/Contents/MacOS/$BIN" "dist/.build/$BIN-arm64" "dist/.build/$BIN-x86_64"
rm -rf dist/.build
echo "    architectures: $(lipo -archs "$APP/Contents/MacOS/$BIN")"

cp ../tools.json "$APP/Contents/Resources/tools.json"

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>$NAME</string>
  <key>CFBundleDisplayName</key><string>$NAME</string>
  <key>CFBundleExecutable</key><string>$BIN</string>
  <key>CFBundleIdentifier</key><string>io.github.cuttingthru18-cmd.ai-slot-tool-finder</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>$VERSION</string>
  <key>CFBundleVersion</key><string>$VERSION</string>
  <key>LSMinimumSystemVersion</key><string>13.0</string>
  <!-- Menu bar only: no Dock icon, no window in the app switcher. -->
  <key>LSUIElement</key><true/>
  <key>NSHighResolutionCapable</key><true/>
</dict>
</plist>
PLIST

# Sign ad-hoc, DEEPLY. An unsigned bundle with a broken seal is what makes macOS say
# "damaged and can't be opened" — which sends users to the Trash instead of to the app.
# This will not clear Gatekeeper on a downloaded copy (that needs a paid Developer ID),
# but it does make the bundle internally valid, so the only thing left is quarantine.
echo "==> signing (ad-hoc)"
codesign --force --deep --sign - "$APP" 2>/dev/null
codesign --verify --deep --strict "$APP" && echo "    signature valid"

echo "==> built: $APP"
du -sh "$APP" | awk '{print "    size: "$1}'

if [ "${1:-}" = "--install" ]; then
  echo "==> installing"
  # Wait for the old copy to actually die. `open` straight after `pkill` races the
  # shutdown and LaunchServices answers -600 (procNotFound), which looks like a
  # broken build when it is only impatience.
  pkill -f "$BIN" 2>/dev/null || true
  for _ in $(seq 1 20); do pgrep -f "$BIN" >/dev/null || break; sleep 0.1; done
  rm -rf "/Applications/$NAME.app"
  cp -R "$APP" /Applications/
  xattr -dr com.apple.quarantine "/Applications/$NAME.app" 2>/dev/null || true
  open -a "/Applications/$NAME.app"
  echo "    installed and launched — look for 🎰 in your menu bar"
fi
