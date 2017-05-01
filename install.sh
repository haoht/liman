#!/bin/bash
#Simple installer for Liman Script Manager
#Still in early development
#Checkout github.com/liman or liman.space for more.

#Check if script run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root"
   exit 1
fi

#Determine OS
if [ "$(uname)" == "Darwin" ]; then
    echo "macOS detected"
    isLinux=false
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    echo "GNU/Linux detected"
    isLinux=true
else
    echo "Sorry, we don't support your operating system."
    exit 1
fi

#Download the liman python file
limanLocation="https://raw.githubusercontent.com/liman/liman/master/bin/liman.py"
if [ "$isLinux" = true ]; then
    wget "$limanLocation"
else
    curl "$limanLocation"
fi

#Check if git installed or not.
if [ "$(which git)" == "" ]; then
    echo "Git is mandatory for liman, installing now."
    #Installing git
    if [ "$isLinux" = true ]; then
        apt-get -y install git
    else
        git
    fi
fi

#Clearing old liman binary.
rm -f /usr/bin/liman

#Copying binary into /usr/bin for global access to command.
mv liman.py /usr/bin/liman
chmod +x /usr/bin/liman

#Preparing liman with default repository
mkdir -p /usr/local/share/liman/

echo "Installing default repositories"
liman add liman/ldepo
echo "Liman installed, default repository added"
