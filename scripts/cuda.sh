#!/bin/bash
set -e

echo "🧹 Uninstalling current CUDA version..."
sudo apt-get --purge remove "*cublas*" "*cufft*" "*curand*" "*cusolver*" "*cusparse*" "*npp*" "*nvjpeg*" "cuda*" "nsight*" "libcudnn*" -y
sudo apt-get autoremove -y
sudo rm -rf /usr/local/cuda*
echo "✅ CUDA removed"

echo "📦 Downloading CUDA 12.3 installer..."
wget https://developer.download.nvidia.com/compute/cuda/12.3.0/local_installers/cuda_12.3.0_535.54.03_linux.run
chmod +x cuda_12.3.0_535.54.03_linux.run

echo "🚀 Installing CUDA 12.3 Toolkit..."
sudo ./cuda_12.3.0_535.54.03_linux.run --silent --toolkit
echo "✅ CUDA 12.3 installed"

# Make sure environment variables are set
if ! grep -q 'cuda-12.3' ~/.bashrc; then
  echo "🔧 Setting environment variables..."
  echo 'export PATH=/usr/local/cuda-12.3/bin:$PATH' >> ~/.bashrc
  echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.3/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
  source ~/.bashrc
fi

echo "🧪 Verifying nvcc..."
nvcc --version

echo "📂 Please download cuDNN 8.9.7 for CUDA 12 (Linux .tar.xz) manually:"
echo "👉 https://developer.nvidia.com/rdp/cudnn-download"

echo "⚠️ Place the downloaded cuDNN file (e.g., cudnn-linux-x86_64-8.9.7.0_cuda12-archive.tar.xz) in this directory."
read -p "🔄 Press [Enter] once you've placed the cuDNN archive here..."

# Detect archive name
CUDNN_ARCHIVE=$(ls cudnn-*-archive.tar.xz | head -n1)
if [[ ! -f "$CUDNN_ARCHIVE" ]]; then
  echo "❌ cuDNN archive not found. Exiting."
  exit 1
fi

echo "📦 Installing cuDNN 8.9.7 from $CUDNN_ARCHIVE..."
tar -xf "$CUDNN_ARCHIVE"
cd cudnn-*-archive
sudo cp include/cudnn*.h /usr/local/cuda/include/
sudo cp lib/libcudnn* /usr/local/cuda/lib64/
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
cd ..

echo "✅ cuDNN installed successfully"

echo "🧪 Verifying cuDNN version:"
grep -A2 CUDNN_MAJOR /usr/local/cuda/include/cudnn_version.h

echo "✅ Setup complete! Ready for TensorFlow 2.19."
#