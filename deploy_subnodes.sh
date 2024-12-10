#!/usr/bin/env bash

# Bu dosya operatör sunucusunda çalışacak.
# subnodes.env dosyasını dahil ediyoruz.
source subnodes.env

# Şimdilik sadece arun üzerinde deneme yapacağız.
ARUN_IP="152.53.33.94"
# Arun'un değişkenleri:
USER_BOT_TOKEN="7307063683:AAEjaKyOdnPAKUaNMbdH0fYvasQvaYdIvJ8"
USER_CHAT_ID="6706302640"
OPERATOR_BOT_TOKEN="7014573028:AAEZqARcPde7rUEcAZdePJudkU6UG8u0gGc"
OPERATOR_CHAT_ID="1686175963"
NODE_NAME="arun"

# setup_subnode.sh'yi indir
wget -O setup_subnode.sh https://raw.githubusercontent.com/halilunay/humanode/refs/heads/main/setup_subnode.sh

# setup_subnode.sh'yi arun'a kopyala
scp setup_subnode.sh root@$ARUN_IP:/root/setup_subnode.sh

# Alt sunucuda scripti çalıştır
ssh root@$ARUN_IP "bash /root/setup_subnode.sh $USER_BOT_TOKEN $USER_CHAT_ID $OPERATOR_BOT_TOKEN $OPERATOR_CHAT_ID $NODE_NAME"

echo "Arun kurulumu tamamlandı!"

