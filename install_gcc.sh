#!/bin/bash

set -e

echo "🔧 Installing GCC 8 and G++ 8..."

# Update Paketliste
sudo apt update

# Installiere GCC 8 und G++ 8
sudo apt install -y gcc-8 g++-8

# Als Standard festlegen
echo "⚙️ Setting GCC 8 and G++ 8 as default..."

sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 80
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-8 80

# Optional: automatisch auswählen, wenn nur eine Version existiert
sudo update-alternatives --set gcc /usr/bin/gcc-8
sudo update-alternatives --set g++ /usr/bin/g++-8

# Version anzeigen
echo -n "✅ GCC version: "
gcc --version | head -n1

echo -n "✅ G++ version: "
g++ --version | head -n1

echo "🎉 Done! GCC 8.4 ist nun aktiv."
