#!/bin/bash

INSTALL_DIR="$HOME/.flux"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_URL="https://raw.githubusercontent.com/YOUR_USERNAME/flux-shell/main"

echo "Installing Flux Shell..."
mkdir -p "$INSTALL_DIR"

if [ -f "$SCRIPT_DIR/main.py" ] && [ -f "$SCRIPT_DIR/config.py" ] && [ -f "$SCRIPT_DIR/ai.py" ]; then
    cp "$SCRIPT_DIR/main.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/config.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/ai.py" "$INSTALL_DIR/"
else
    curl -s "$REPO_URL/main.py" -o "$INSTALL_DIR/main.py"
    curl -s "$REPO_URL/config.py" -o "$INSTALL_DIR/config.py"
    curl -s "$REPO_URL/ai.py" -o "$INSTALL_DIR/ai.py"
fi

echo "Installing Python dependencies..."
python3 -m pip install prompt_toolkit rich --break-system-packages 2>/dev/null || pip install prompt_toolkit rich

add_autostart() {
    local rc_file="$1"
    if [ -f "$rc_file" ] || [ "$2" = "force" ]; then
        touch "$rc_file"
        if ! grep -q "python3 $INSTALL_DIR/main.py" "$rc_file"; then
            echo -e "\n# Flux Shell Autostart" >> "$rc_file"
            echo 'if [ -z "$FLUX_ACTIVE" ]; then' >> "$rc_file"
            echo '    export FLUX_ACTIVE=1' >> "$rc_file"
            echo "    exec python3 $INSTALL_DIR/main.py" >> "$rc_file"
            echo 'fi' >> "$rc_file"
        fi
    fi
}

add_autostart "$HOME/.bashrc" "force"
add_autostart "$HOME/.zshrc" "optional"

KITTY_CONF="$HOME/.config/kitty/kitty.conf"
if [ -d "$HOME/.config/kitty" ]; then
    if ! grep -q "confirm_os_window_close" "$KITTY_CONF" 2>/dev/null; then
        echo "confirm_os_window_close 0" >> "$KITTY_CONF"
    fi
fi

echo "Installation complete! Restart terminal or open a new window to start Flux Shell."