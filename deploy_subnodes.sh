#!/usr/bin/env bash

source subnodes.env

# Örnek varsayılan operatör bilgileri (tüm sunucular için aynı)
OPERATOR_BOT_TOKEN="123456:ABC-OperatorBotToken"
OPERATOR_CHAT_ID="333333333"

# node1 bilgileri:
NODE1_IP="10.10.10.11"
NODE1_USER_BOT_TOKEN="123456:ABC-User1BotToken"
NODE1_USER_CHAT_ID="111111111"
NODE1_NODE_NAME="node1"

# node2 bilgileri:
NODE2_IP="10.10.10.12"
NODE2_USER_BOT_TOKEN="123456:ABC-User2BotToken"
NODE2_USER_CHAT_ID="222222222"
NODE2_NODE_NAME="node2"

# node3 bilgileri (kullanıcısı yok):
NODE3_IP="10.10.10.13"
NODE3_USER_BOT_TOKEN=""
NODE3_USER_CHAT_ID=""
NODE3_NODE_NAME="node3"

wget -O setup_subnode.sh https://raw.githubusercontent.com/KENDI_GITHUB_KULLANICI_ADIN/Humanode/main/setup_subnode.sh

deploy_one_subnode() {
  local IP="$1"
  local UBT="$2"
  local UCI="$3"
  local OBT="$4"
  local OCI="$5"
  local NAME="$6"

  echo "==> $NAME ($IP) sunucusuna kurulum başlıyor..."
  scp setup_subnode.sh root@$IP:/root/setup_subnode.sh
  ssh root@$IP "bash /root/setup_subnode.sh $UBT $UCI $OBT $OCI $NAME"
  echo "==> $NAME kurulumu tamamlandı!"
}

# node1 kurulumu
deploy_one_subnode $NODE1_IP $NODE1_USER_BOT_TOKEN $NODE1_USER_CHAT_ID $OPERATOR_BOT_TOKEN $OPERATOR_CHAT_ID $NODE1_NODE_NAME

# node2 kurulumu
deploy_one_subnode $NODE2_IP $NODE2_USER_BOT_TOKEN $NODE2_USER_CHAT_ID $OPERATOR_BOT_TOKEN $OPERATOR_CHAT_ID $NODE2_NODE_NAME

# node3 kurulumu (kullanıcısı yok, sessiz modda çalışır)
deploy_one_subnode $NODE3_IP $NODE3_USER_BOT_TOKEN $NODE3_USER_CHAT_ID $OPERATOR_BOT_TOKEN $OPERATOR_CHAT_ID $NODE3_NODE_NAME

echo "Tüm sunucular için kurulum tamamlandı!"
