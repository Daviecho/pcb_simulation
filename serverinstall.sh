#!/bin/bash

# Update and upgrade system packages
#echo "Updating system packages..."
#sudo apt-get update && sudo apt-get upgrade -y #optional


# Install SimPy
echo "Installing ..."
pip install --break-system-packages simpy

echo "Installing PyTorch Geometric..."
pip install --break-system-packages torch torchvision torchaudio
pip install --break-system-packages torch-geometric
pip install --break-system-packages python-dotenv

# Install TensorBoard
pip install --break-system-packages tensorboard
pip install --break-system-packages optuna
pip install --break-system-packages matplotlib

# git clone https://github.com/Daviecho/pcb_simulation.git

chmod +x main.py
chmod +x opt.py

echo "Installation script completed."
#scp -r ubuntu@sdm:~/pcb_simulation/tensorb .
# tensorboard --logdir=runs

#What I tried to make CUDA work
# sudo apt purge '^nvidia-.*'
# sudo apt autoremove
# sudo apt update
# sudo apt install nvidia-driver-535
# sudo reboot
# sudo apt install linux-headers-$(uname -r)
# sudo apt upgrade
# sudo prime-select nvidia
#pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu122

#72.46.85.107
