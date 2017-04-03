#!/bin/bash
#Simple installer for Liman Script Manager
#Still in early development

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root"
   exit 1
fi

cp bin/liman.py /usr/bin/liman
chmod +x /usr/bin/liman
mkdir -p /usr/local/share/liman/

echo "Let's install default repositories as well"
liman add liman/liman-depo
#clear
echo "Liman installed, default repository added"
