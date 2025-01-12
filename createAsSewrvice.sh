#!/bin/bash

# Variables
SERVICE_NAME="optFS"           # Replace with your desired service name
SCRIPT_PATH="/root/pcb_simulation/opt.py"      # Full path to your Python script
WORKING_DIR="/root/pcb_simulation"  # Directory where the script resides
LOG_DIR="/var/log"                   # Directory for logs
OUTPUT_LOG="$LOG_DIR/log_optFS.log"
ERROR_LOG="$LOG_DIR/error_optFS.log"

# Ensure the script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# Create log directory if it doesn't exist
if [ ! -d "$LOG_DIR" ]; then
    echo "Creating log directory at $LOG_DIR"
    mkdir -p "$LOG_DIR"
fi

# Create the service file
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Creating service file at $SERVICE_FILE"
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Run my Python script as a service
After=network.target

[Service]
ExecStart=/usr/bin/python3 $SCRIPT_PATH
WorkingDirectory=$WORKING_DIR
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"
StandardOutput=append:$OUTPUT_LOG
StandardError=append:$ERROR_LOG

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd, start, and enable the service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# echo "Starting the service..."
# sudo systemctl start $SERVICE_NAME

# echo "Enabling the service to start on boot..."
# sudo systemctl enable $SERVICE_NAME

# Check service status
echo "Checking service status..."
sudo systemctl status $SERVICE_NAME

# Done
echo "Service setup complete. Logs will be written to:"
echo "  Output: $OUTPUT_LOG"
echo "  Errors: $ERROR_LOG"
