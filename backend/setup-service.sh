#!/bin/bash

# Setup script for PMS Backend Service
# This script will install the backend as a systemd service

SERVICE_NAME="pms-backend"
SERVICE_FILE="pms-backend.service"
CURRENT_DIR=$(pwd)
SERVICE_PATH="$CURRENT_DIR/$SERVICE_FILE"

echo "Setting up PMS Backend Service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo"
    exit 1
fi

# Copy service file to systemd directory
echo "Installing service file..."
cp "$SERVICE_PATH" /etc/systemd/system/

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling service to start on boot..."
systemctl enable "$SERVICE_NAME"

echo "Service setup complete!"
echo ""
echo "To manage the service, use these commands:"
echo "  Start service:   sudo systemctl start $SERVICE_NAME"
echo "  Stop service:    sudo systemctl stop $SERVICE_NAME"
echo "  Restart service: sudo systemctl restart $SERVICE_NAME"
echo "  Check status:    sudo systemctl status $SERVICE_NAME"
echo "  View logs:       sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "The service will now start automatically on system boot." 