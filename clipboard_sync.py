import hashlib
import json
import os
import socket
import sys
import threading
import time
from typing import Optional

import pyperclip
from azure.servicebus import ServiceBusClient, ServiceBusMessage


SB_CONNECTION_STRING = os.environ.get("SB_CONNECTION_STRING", "").strip()
SB_QUEUE_NAME = os.environ.get("SB_QUEUE_NAME", "").strip()
DEVICE_ID = os.environ.get("DEVICE_ID", "").strip() or socket.gethostname()
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "0.8"))
RECV_WAIT_SECONDS = float(os.environ.get("RECV_WAIT_SECONDS", "5"))
SUPPRESS_SECONDS = float(os.environ.get("SUPPRESS_SECONDS", "2.5"))
MAX_CONTENT_LEN = int(os.environ.get("MAX_CONTENT_LEN", "200000"))


def require_env():
    missing = []
    if not SB_CONNECTION_STRING:
        missing.append("SB_CONNECTION_STRING")
    if not SB_QUEUE_NAME:
        missing.append("SB_QUEUE_NAME")
    if missing:
        print(f"Missing env: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def now_ts() -> float:
    return time.time()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class State:
    def __init__(self):
        self.last_local_text: str = ""
        self.last_local_hash: str = ""
        self.last_remote_hash: str = ""
        self.suppress_until: float = 0.0
        self.lock = threading.Lock()

    def set_remote_applied(self, text: str):
        h = sha256_text(text)
        with self.lock:
            self.last_remote_hash = h
            self.last_local_text = text
            self.last_local_hash = h
            self.suppress_until = now_ts() + SUPPRESS_SECONDS

    def set_local_seen(self, text: str):
        h = sha256_text(text)
        with self.lock:
            self.last_local_text = text
            self.last_local_hash = h

    def should_suppress(self) -> bool:
        with self.lock:
            return now_ts() < self.suppress_until

    def current_local_hash(self) -> str:
        with self.lock:
            return self.last_local_hash


state = State()


def safe_paste() -> str:
    try:
        value = pyperclip.paste()
        if value is None:
            return ""
        if not isinstance(value, str):
            value = str(value)
        return value
    except Exception as e:
        print(f"[paste-error] {e}", file=sys.stderr)
        return ""


def safe_copy(text: str):
    try:
        pyperclip.copy(text)
    except Exception as e:
        print(f"[copy-error] {e}", file=sys.stderr)


def build_payload(text: str) -> str:
    payload = {
        "device_id": DEVICE_ID,
        "timestamp": int(now_ts()),
        "content": text,
        "content_hash": sha256_text(text),
    }
    return json.dumps(payload, ensure_ascii=False)


def parse_payload(raw: str) -> Optional[dict]:
    try:
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            return None
        return obj
    except Exception:
        return None


def sender_loop(client: ServiceBusClient):
    sender = client.get_queue_sender(queue_name=SB_QUEUE_NAME)
    with sender:
        initial = safe_paste()
        state.set_local_seen(initial)
        print(f"[startup] device_id={DEVICE_ID} initial_len={len(initial)}")

        while True:
            text = safe_paste()
            current_hash = sha256_text(text)

            if current_hash != state.current_local_hash():
                state.set_local_seen(text)

                if state.should_suppress():
                    print("[local-change] suppressed")
                else:
                    if len(text) > MAX_CONTENT_LEN:
                        print(f"[skip] clipboard too large len={len(text)}")
                    else:
                        payload = build_payload(text)
                        sender.send_messages(ServiceBusMessage(payload))
                        print(f"[sent] len={len(text)} hash={current_hash[:12]}")

            time.sleep(POLL_INTERVAL)


def receiver_loop(client: ServiceBusClient):
    receiver = client.get_queue_receiver(queue_name=SB_QUEUE_NAME, max_wait_time=RECV_WAIT_SECONDS)
    with receiver:
        while True:
            try:
                messages = receiver.receive_messages(max_message_count=10, max_wait_time=RECV_WAIT_SECONDS)
                if not messages:
                    continue

                for msg in messages:
                    try:
                        raw = b"".join([bytes(part) if not isinstance(part, bytes) else part for part in msg.body]).decode("utf-8")
                    except Exception:
                        raw = str(msg)

                    payload = parse_payload(raw)
                    if not payload:
                        print("[recv-skip] invalid payload")
                        receiver.complete_message(msg)
                        continue

                    device_id = str(payload.get("device_id", ""))
                    content = payload.get("content", "")
                    if not isinstance(content, str):
                        content = str(content)

                    content_hash = str(payload.get("content_hash", sha256_text(content)))

                    if device_id == DEVICE_ID:
                        print(f"[recv-self] skip hash={content_hash[:12]}")
                        receiver.complete_message(msg)
                        continue

                    if content_hash == state.current_local_hash():
                        print(f"[recv-same] skip hash={content_hash[:12]}")
                        receiver.complete_message(msg)
                        continue

                    safe_copy(content)
                    state.set_remote_applied(content)
                    print(f"[applied] from={device_id} len={len(content)} hash={content_hash[:12]}")
                    receiver.complete_message(msg)
            except Exception as e:
                print(f"[recv-error] {e}", file=sys.stderr)
                time.sleep(2)


def main():
    require_env()
    client = ServiceBusClient.from_connection_string(conn_str=SB_CONNECTION_STRING, logging_enable=False)

    t1 = threading.Thread(target=sender_loop, args=(client,), daemon=True)
    t2 = threading.Thread(target=receiver_loop, args=(client,), daemon=True)
    t1.start()
    t2.start()

    print("[running] clipboard sync started")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\n[shutdown] bye")


if __name__ == "__main__":
    main()
