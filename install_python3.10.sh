#!/bin/bash

set -e

echo "🚀 Python 3.10 auf Jetson"

# 1. Install Python 3.10 from source
echo "📦 Installiere Abhängigkeiten..."
sudo apt update
sudo apt install -y build-essential libssl-dev zlib1g-dev \
  libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
  libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev \
  wget curl git libffi-dev

echo "⬇️ Lade Python 3.10.13..."
cd /tmp
wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tgz
tar -xf Python-3.10.13.tgz
cd Python-3.10.13

echo "🔨 Baue Python 3.10 (kann 5–10 Minuten dauern)..."
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall  # installiert als python3.10, ohne alte Version zu überschreiben