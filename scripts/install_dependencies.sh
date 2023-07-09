#!/bin/bash
# This script will install the app's dependencies and setup the service.

# Navigate to app directory
cd /opt/my_app

# Install dependencies
pip install -r requirements.txt

# Check if the service file exists
if [ ! -f /etc/systemd/system/webapi.service ]; then
  # Create the service file
  cat << EOF > /etc/systemd/system/webapi.service
  [Unit]
  Description=Web API
  After=network.target

  [Service]
  ExecStart=python3 main.py
  WorkingDirectory=/opt/my_app
  User=ubuntu
  Group=www-data
  Restart=always

  [Install]
  WantedBy=multi-user.target
EOF

  # Reload the systemd daemon
  systemctl daemon-reload

  # Enable the service to start on boot
  systemctl enable webapi
fi
