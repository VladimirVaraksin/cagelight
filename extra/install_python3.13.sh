#!/bin/bash

set -e

echo "🔄 System aktualisieren..."
sudo apt update
sudo apt upgrade -y

echo "📦 Abhängigkeiten installieren..."
sudo apt install -y \
  build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev \
  libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev \
  libexpat1-dev liblzma-dev tk-dev wget curl git libffi-dev uuid-dev

echo "⬇️ Python 3.13 herunterladen..."
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz
sudo tar xzf Python-3.13.0.tgz
cd Python-3.13.0

echo "⚙️ Python 3.13 konfigurieren und bauen..."
sudo ./configure --enable-optimizations
sudo make -j$(nproc)

echo "📥 Python 3.13 installieren..."
sudo make altinstall

echo "✅ Installation abgeschlossen!"
python3.13 --version
