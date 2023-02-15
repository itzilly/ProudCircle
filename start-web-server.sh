#!/bin/bash

cd web-server/env/bin
source activate
cd ../..

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

# Start the server
cd web-server/src
python main.py
