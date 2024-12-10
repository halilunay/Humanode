#!/usr/bin/env bash

USER_BOT_TOKEN="$1"
USER_CHAT_ID="$2"
OPERATOR_BOT_TOKEN="$3"
OPERATOR_CHAT_ID="$4"
NODE_NAME="$5"

apt-get update -y && apt-get upgrade -y
apt-get install -y curl wget tar ufw python3 python3-pip
python3 -m pip install --upgrade pip
python3 -m pip install python-telegram-bot==13.14 requests

useradd --no-create-home --shell /bin/false node_exporter || true
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvf node_exporter-1.6.1.linux-amd64.tar.gz
mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
chown node_exporter:node_exporter /usr/local/bin/node_exporter

cat <<EOF >/etc/systemd/system/node_exporter.service
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start node_exporter
systemctl enable node_exporter
ufw allow 9100/tcp

cat <<EOF >/root/check_all.env
USER_BOT_TOKEN=$USER_BOT_TOKEN
USER_CHAT_ID=$USER_CHAT_ID
OPERATOR_BOT_TOKEN=$OPERATOR_BOT_TOKEN
OPERATOR_CHAT_ID=$OPERATOR_CHAT_ID
NODE_NAME=$NODE_NAME
EOF

wget -O /root/check_all.py https://raw.githubusercontent.com/halilunay/humanode/refs/heads/main/check_all.py
chmod +x /root/check_all.py

cat <<EOF >/etc/systemd/system/check_all.service
[Unit]
Description=Check all metrics and notify
After=network.target

[Service]
User=root
WorkingDirectory=/root
EnvironmentFile=/root/check_all.env
ExecStart=/usr/bin/python3 /root/check_all.py

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF >/etc/systemd/system/check_all.timer
[Unit]
Description=Run check_all script every 1 minute

[Timer]
OnBootSec=30
OnUnitActiveSec=60

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl start check_all.timer
systemctl enable check_all.timer

echo "Kurulum tamamlandı!"
