#!/bin/bash

set -e

echo "🚀 Installiere Python 3.12 auf Jetson"

# 1. Installiere Abhängigkeiten
echo "📦 Installiere Abhängigkeiten..."
sudo apt update
sudo apt install -y build-essential libssl-dev zlib1g-dev \
  libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
  libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev \
  wget curl git libffi-dev

# 2. Lade und entpacke Python 3.12
PYTHON_VERSION=3.12.3
echo "⬇️ Lade Python $PYTHON_VERSION..."
cd /tmp
wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
tar -xf Python-${PYTHON_VERSION}.tgz
cd Python-${PYTHON_VERSION}

# 3. Kompiliere und installiere
echo "🔨 Baue Python $PYTHON_VERSION (kann einige Minuten dauern)..."
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall  # installiert z.B. als python3.12, ohne bestehende Versionen zu ersetzen

echo "✅ Python $PYTHON_VERSION wurde erfolgreich installiert!"
python3.12 --version
