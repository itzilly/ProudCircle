#!/bin/bash

VENV_DIR="web-server/env"

python_version=$(python3 -c "import platform; print(platform.python_version())")
required_version="3.8.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Python version must be at least $required_version"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# Check for installed packages
requirements_installed=true
while read -r package; do
    pip list --format=freeze | grep -i "$package" >/dev/null
    if [ "$?" -ne 0 ]; then
        requirements_installed=false
        pip install "$package"
    fi
done < web-server/requirements.txt

if [ "$requirements_installed" = false ]; then
    pip install -r web-server/requirements.txt
fi

# Start web server
cd web-server/src
python main.py
