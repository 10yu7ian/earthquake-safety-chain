"""批量向后端上报 restore 事件（无需登录；用于联调或批量恢复设备状态）。"""

import requests

BASE_URL = "http://localhost:8000"
DEVICE_IDS = ["LM-1001", "LM-1002", "LM-1003", "LM-1004", "LM-1005"]
TIMESTAMP = "2026-05-05T15:00:00Z"


def main() -> None:
    for device_id in DEVICE_IDS:
        payload = {
            "device_id": device_id,
            "event_type": "restore",
            "acc_max": 0.0,
            "timestamp": TIMESTAMP,
        }
        resp = requests.post(f"{BASE_URL}/api/event", json=payload, timeout=10)
        print(f"{device_id}: HTTP {resp.status_code}")


if __name__ == "__main__":
    main()
