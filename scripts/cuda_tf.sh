#!/bin/bash
set -e

echo "🔧 Setting up persistent TensorFlow GPU Docker environment..."

# 1. Create project workspace
WORKDIR=~/tensorflow_gpu_workspace
mkdir -p "$WORKDIR"
echo "✅ Created workspace at $WORKDIR"

# 2. Create a Dockerfile with extra packages
cat > "$WORKDIR/Dockerfile" <<EOF
FROM tensorflow/tensorflow:2.13.0-gpu-jupyter

# Install additional Python packages
RUN pip install matplotlib pandas scikit-learn seaborn
EOF
echo "✅ Dockerfile created"

# 3. Build Docker image
cd "$WORKDIR"
docker build -t tf-gpu-dev .
echo "✅ Docker image 'tf-gpu-dev' built"

# 4. Run the Docker container with GPU, Jupyter, and persistent volume
docker run -it --gpus all \
  -v "$WORKDIR":/tf \
  -p 8888:8888 \
  --name tf-gpu-container \
  tf-gpu-dev \
  jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --NotebookApp.token=''
