#!/bin/bash

set -e

echo "🚀 Python 3.10, PyTorch & Ultralytics Installation auf Jetson"

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

# 2. Erstelle venv
cd ~
python3.10 -m venv yolovenv
source yolovenv/bin/activate

# 3. Installiere pip & wheel
echo "📦 Upgrade pip & tools..."
python -m ensurepip
pip install --upgrade pip setuptools wheel

# 4. Installiere PyTorch für Jetson (Python 3.10, JetPack 5.1+, CUDA 11.4)
echo "⬇️ Lade PyTorch für Jetson (Python 3.10)..."
wget https://nvidia.box.com/shared/static/q1crw1ixq5kehlkz22j0z5h7yt7np63f.whl -O torch-2.0.0-cp310-cp310-linux_aarch64.whl

echo "📦 Installiere PyTorch..."
pip install torch-2.0.0-cp310-cp310-linux_aarch64.whl

# 5. Installiere ultralytics
echo "📦 Installiere ultralytics (YOLOv8)..."
pip install ultralytics

# 6. Test
echo "✅ Test: Torch & YOLO"
python -c "import torch; print('Torch ✅', torch.__version__)"
python -c "from ultralytics import YOLO; print('Ultralytics ✅')"

echo "🎉 Fertig! Python 3.10, PyTorch & ultralytics sind installiert und einsatzbereit."
