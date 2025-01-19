#!/bin/bash

# Installer for combine-files tool

# Default installation directory
INSTALL_DIR="/usr/local/opt/combine-files"
BIN_LINK="/usr/local/bin/combine-files"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Installing combine-files tool...${NC}"

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"/{bin,lib,config,automator}

# Copy files
echo "Copying files..."
cp -f bin/combine-files "$INSTALL_DIR/bin/"
cp -f lib/combine_files.py "$INSTALL_DIR/lib/"
cp -f config/default_excludes.txt "$INSTALL_DIR/config/"

# Set permissions
echo "Setting permissions..."
chmod 755 "$INSTALL_DIR/bin/combine-files"
chmod 644 "$INSTALL_DIR/lib/combine_files.py"
chmod 644 "$INSTALL_DIR/config/default_excludes.txt"

# Create symlink
echo "Creating symlink..."
ln -sf "$INSTALL_DIR/bin/combine-files" "$BIN_LINK"

# Create Quick Action
echo "Creating Quick Action..."
QUICK_ACTION_DIR="$HOME/Library/Services"
mkdir -p "$QUICK_ACTION_DIR"

# Create Quick Action workflow
cat > "$QUICK_ACTION_DIR/Combine Files.workflow/Contents/document.wflow" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>521.1</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <false/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>2.0.1</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>source</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>for f in "$@"
do
    /usr/local/bin/combine-files "$f" "$f/combined_files.txt"
done</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                    <key>source</key>
                    <string></string>
                </dict>
            </dict>
        </dict>
    </array>
</dict>
</plist>
EOF

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${BLUE}You can now use:${NC}"
echo "1. Command line: combine-files <input_dir> <output_file>"
echo "2. Finder: Right-click on folder → Quick Actions → Combine Files"
echo
echo -e "${BLUE}Example usage:${NC}"
echo "combine-files ~/myproject output.txt" 