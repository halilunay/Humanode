import os
import re
import requests
import json
import time
from telegram import Bot
import subprocess

USER_BOT_TOKEN = os.environ.get("USER_BOT_TOKEN", "").strip()
USER_CHAT_ID = os.environ.get("USER_CHAT_ID", "").strip()
OPERATOR_BOT_TOKEN = os.environ.get("OPERATOR_BOT_TOKEN", "").strip()
OPERATOR_CHAT_ID = os.environ.get("OPERATOR_CHAT_ID", "").strip()
NODE_NAME = os.environ.get("NODE_NAME", "UnknownNode")

RPC_ENDPOINT = "http://127.0.0.1:9933"
STATE_FILE = "/root/state.json"

# Kullanıcı bilgisi var mı?
# Eğer yoksa hiçbir mesaj gönderilmeyecek.
NOTIFICATIONS_ENABLED = bool(USER_BOT_TOKEN and USER_CHAT_ID)

NOTIFY_TIMES = {
    "12h": 12 * 3600,
    "4h": 4 * 3600,
    "1h": 3600,
    "5m": 300,
    "0s": 0
}

REMINDER_INTERVAL = 3600  # 1 saat

def identify_user_for_operator():
    if USER_CHAT_ID:
        return f"[{NODE_NAME}] (User: {USER_CHAT_ID})"
    else:
        return f"[{NODE_NAME}] (NoUser)"

def send_message_to_user(message):
    # Eğer kullanıcı yoksa mesaj gönderme
    if not NOTIFICATIONS_ENABLED:
        return
    if not USER_BOT_TOKEN or not USER_CHAT_ID:
        return
    bot = Bot(token=USER_BOT_TOKEN)
    bot.send_message(chat_id=USER_CHAT_ID, text=f"[{NODE_NAME}] {message}")

def send_message_to_operator(message):
    # Kullanıcı yoksa operatöre de mesaj gönderme
    # İstenmiyorsa bu satırda da engelleyebiliriz.
    # Mevcut istek: Kullanıcı yoksa tam sessizlik -> Operatöre de mesaj yok.
    if not NOTIFICATIONS_ENABLED:
        return
    if not OPERATOR_BOT_TOKEN or not OPERATOR_CHAT_ID:
        return
    bot = Bot(token=OPERATOR_BOT_TOKEN)
    prefix = identify_user_for_operator()
    bot.send_message(chat_id=OPERATOR_CHAT_ID, text=f"{prefix} {message}")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "last_bioauth_status": None,
        "expires_at": None,
        "notified_times": {
            "12h": False,
            "4h": False,
            "1h": False,
            "5m": False,
            "0s": False
        },
        "last_inactive_notification": 0,
        "last_validator_status": None,
        "last_tunnel_status": None,
        "last_tunnel_notification_time": 0,
        "last_sync_status": None,
        "last_sync_notification_time": 0
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_bioauth_status():
    payload = {"jsonrpc":"2.0","method":"bioauth_status","params":[],"id":1}
    try:
        response = requests.post(RPC_ENDPOINT, json=payload, timeout=5)
        res = response.json().get("result", None)
        if res == "Inactive":
            return "Inactive", None
        if isinstance(res, dict) and "Active" in res:
            expires_at = res["Active"].get("expires_at", None)
            return "Active", expires_at
        return "Unknown", None
    except:
        return "Unknown", None

def get_tunnel_status():
    result = subprocess.run(["pgrep", "-f", "humanode-websocket-tunnel-client"], stdout=subprocess.DEVNULL)
    return "Up" if (result.returncode == 0) else "Down"

def get_tunnel_link():
    log_file = "/root/.humanode/workspaces/default/tunnel/logs.txt"
    if not os.path.exists(log_file):
        return None
    with open(log_file, "rb") as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        size = 1024
        if end < size:
            size = end
        f.seek(-size, os.SEEK_END)
        lines = f.readlines()
    for line in reversed(lines):
        line = line.decode('utf-8', errors='ignore')
        match = re.search(r"wss://[^\s]+", line)
        if match:
            return match.group(0)
    return None

def check_sync_status():
    payload = {"jsonrpc":"2.0","method":"system_syncState","params":[],"id":1}
    try:
        response = requests.post(RPC_ENDPOINT, json=payload, timeout=5)
        data = response.json()
        if 'result' in data:
            current = data['result'].get('currentBlock', 0)
            highest = data['result'].get('highestBlock', 0)
            diff = highest - current
            status = "Synced" if diff <= 6 else "Syncing"
            return status, diff
        return "Unexpected", None
    except:
        return "No response", None

def check_validator_status():
    status, _ = get_bioauth_status()
    if status == "Active":
        return "Active"
    elif status == "Inactive":
        return "Inactive"
    else:
        return "Unknown"

def main():
    state = load_state()
    now = int(time.time())

    current_bioauth_status, expires_at = get_bioauth_status()
    tunnel_status = get_tunnel_status()
    validator_status = check_validator_status()
    sync_status, sync_diff = check_sync_status()

    # Bioauth
    if current_bioauth_status == "Active" and expires_at:
        expire_time = expires_at // 1000
        remaining = expire_time - now
        for label, threshold in NOTIFY_TIMES.items():
            if remaining <= threshold and not state["notified_times"][label]:
                if label == "0s":
                    msg = "Bioauth süreniz doldu. Lütfen tekrar yüz taraması yapınız."
                else:
                    msg = f"Bioauth sürenizin bitmesine {label} kaldı. Lütfen hazırlıklı olun."
                send_message_to_user(msg)
                state["notified_times"][label] = True

    elif current_bioauth_status == "Inactive":
        if state["last_bioauth_status"] == "Active":
            link = get_tunnel_link()
            user_msg = "❌ Bioauth inaktif! Yüz taraması yapmalısınız."
            if link:
                user_msg += f"\nTaramayı yapmak için link: https://webapp.mainnet.stages.humanode.io/open?url={link}"
            send_message_to_user(user_msg)
            send_message_to_operator("Bioauth inaktif oldu. " + user_msg)
            state["last_inactive_notification"] = now
        else:
            if now - state["last_inactive_notification"] >= 600:
                link = get_tunnel_link()
                user_msg = "❌ Bioauth hala inaktif! Lütfen yüz taramanızı yapın."
                if link:
                    user_msg += f"\nLink: https://webapp.mainnet.stages.humanode.io/open?url={link}"
                send_message_to_user(user_msg)
                send_message_to_operator("Bioauth hala inaktif. Kullanıcı tekrar bilgilendirildi.")
                state["last_inactive_notification"] = now

    if state["last_bioauth_status"] == "Inactive" and current_bioauth_status == "Active":
        send_message_to_user("✅ Bioauth işleminiz tekrar aktif! Teşekkürler.")
        send_message_to_operator("Bioauth tekrar aktif edildi. Kullanıcı yüz taramasını yaptı.")
        for k in state["notified_times"].keys():
            state["notified_times"][k] = False

    # Validator
    last_validator = state.get("last_validator_status", None)
    if validator_status == "Inactive":
        if last_validator != "Inactive":
            send_message_to_operator("Validator Inactive durumda. Lütfen kontrol edin.")

    # Tunnel
    last_tunnel = state.get("last_tunnel_status", None)
    last_tunnel_notif = state.get("last_tunnel_notification_time", 0)

    if tunnel_status == "Down":
        if last_tunnel != "Down":
            send_message_to_operator("⚠️ RPC Tunnel kapalı. Müdahale gerekebilir.")
            state["last_tunnel_notification_time"] = now
        else:
            if now - last_tunnel_notif >= REMINDER_INTERVAL:
                send_message_to_operator("⚠️ RPC Tunnel hala kapalı! Lütfen müdahale edin.")
                state["last_tunnel_notification_time"] = now
    else:
        if last_tunnel == "Down":
            send_message_to_operator("RPC Tunnel tekrar aktif. Müdahaleniz başarılı oldu.")

    # Sync
    last_sync = state.get("last_sync_status", None)
    last_sync_notif = state.get("last_sync_notification_time", 0)

    if sync_status == "Syncing":
        if last_sync != "Syncing":
            if sync_diff is not None:
                send_message_to_operator(f"Node senkronize değil. Fark: {sync_diff} blok.")
            else:
                send_message_to_operator("Node senkronize değil.")
            state["last_sync_notification_time"] = now
        else:
            if now - last_sync_notif >= REMINDER_INTERVAL:
                if sync_diff is not None:
                    send_message_to_operator(f"Node hala senkronize değil. Fark: {sync_diff} blok.")
                else:
                    send_message_to_operator("Node hala senkronize değil.")
                state["last_sync_notification_time"] = now
    elif sync_status == "Synced":
        if last_sync == "Syncing":
            send_message_to_operator("Node tekrar senkronize oldu. Müdahaleniz sonuç verdi.")

    # State Güncelle
    state["last_validator_status"] = validator_status
    state["last_bioauth_status"] = current_bioauth_status
    if current_bioauth_status == "Active":
        state["expires_at"] = expires_at

    state["last_tunnel_status"] = tunnel_status
    state["last_sync_status"] = sync_status

    save_state(state)

if __name__ == "__main__":
    main()
