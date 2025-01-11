#!/bin/bash

# Update and upgrade system packages
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y


# Install SimPy
echo "Installing SimPy..."
pip install simpy

# Install PyTorch Geometric and its dependencies
echo "Installing PyTorch Geometric..."
pip install torch torchvision torchaudio
pip install torch-geometric

# Install TensorBoard
echo "Installing TensorBoard..."
pip install tensorboard

echo "Installation script completed."
