import os
import random
import threading
import time
import traceback
from datetime import datetime, timezone
from typing import Optional

import requests

from sct_api import post_sct_send

BASE_URL = "http://localhost:8000"
SCT_SEND_KEY = os.getenv("SERVERCHAN_KEY")
DEVICE_IDS = ["LM-1001", "LM-1002", "LM-1003", "LM-1004", "LM-1005"]

LOOP_INTERVAL_SECONDS = float(os.environ.get("SIMULATE_PI_LOOP_INTERVAL", "10"))
POLL_INTERVAL_SECONDS = float(os.environ.get("SIMULATE_PI_POLL_INTERVAL", "5"))

# 非第 14 轮：shutdown 3%，restore 1%，check 1%，其余无事件
PROB_SHUTDOWN = 0.03
PROB_RESTORE = 0.04  # 累计阈：0.03~0.04 为 restore
PROB_CHECK = 0.05  # 累计阈：0.04~0.05 为 check


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str) -> None:
    print(f"[{now_text()}] {message}")


def send_wechat_shutdown(payload: dict) -> None:
    """仅在 shutdown 时通过微信推送（Server酱）。"""
    if not SCT_SEND_KEY:
        log("警告: 环境变量 SERVERCHAN_KEY 未设置，跳过微信推送")
        return
    try:
        desp = (
            f"设备ID: {payload['device_id']}\n"
            f"峰值加速度: {payload['acc_max']} g\n"
            f"触发时间: {payload['timestamp']}"
        )
        resp = post_sct_send(
            SCT_SEND_KEY,
            "【地震安链】地震预警 - 燃气已切断",
            desp,
            timeout=15,
        )
        if not resp.ok:
            log(f"微信推送失败: HTTP {resp.status_code} {resp.text[:500]}")
    except requests.RequestException as exc:
        log(f"微信推送失败: {exc}")


def notify_exception_log(where: str, exc: BaseException) -> None:
    """异常仅打日志，不触发微信（与「仅 shutdown 推送」一致）。"""
    tb = traceback.format_exc() or repr(exc)
    if len(tb) > 3500:
        tb = tb[:3500] + "\n…(已截断)"
    log(f"异常 @ {where}: {exc!r}\n{tb}")


def build_acc_max(event_type: str) -> float:
    if event_type == "shutdown":
        return round(random.uniform(2.5, 5.0), 2)
    if event_type == "restore":
        return round(random.uniform(0.1, 1.2), 2)
    return round(random.uniform(0.1, 2.0), 2)


def post_event(
    session: requests.Session,
    device_id: str,
    event_type: str,
    acc_max: Optional[float] = None,
    *,
    force_note: str = "",
) -> None:
    payload = {
        "device_id": device_id,
        "event_type": event_type,
        "acc_max": build_acc_max(event_type) if acc_max is None else acc_max,
        "timestamp": now_iso(),
    }
    prefix = f"{force_note} " if force_note else ""
    log(f"{prefix}上报事件 — 设备 {device_id}, 类型 {event_type}")
    try:
        resp = session.post(f"{BASE_URL}/api/event", json=payload, timeout=8)
        log(f"上报响应状态码: {resp.status_code}")
    except requests.RequestException as exc:
        log(f"上报失败: {exc}")
        return

    if event_type == "shutdown":
        send_wechat_shutdown(payload)


def poll_worker(stop_event: threading.Event) -> None:
    """轮询远程复位：前端下发 reset / restore 后上报 restore。"""
    session = requests.Session()
    last_restore_report_time = {}
    while not stop_event.is_set():
        for device_id in DEVICE_IDS:
            command_text = "无"
            try:
                resp = session.get(
                    f"{BASE_URL}/api/control/poll",
                    params={"device_id": device_id},
                    timeout=8,
                )
                if resp.ok:
                    data = resp.json()
                    command_text = data.get("command") or "无"
                else:
                    command_text = f"请求失败({resp.status_code})"
            except requests.RequestException as exc:
                command_text = f"请求异常({exc})"
            except ValueError:
                command_text = "响应不是合法 JSON"

            log(f"[poll] 设备 {device_id} 指令: {command_text}")
            if command_text in ("restore", "reset"):
                now_ts = time.time()
                last_ts = last_restore_report_time.get(device_id, 0)
                if now_ts - last_ts >= 3:
                    post_event(session, device_id, "restore", acc_max=0.0, force_note="[poll]")
                    last_restore_report_time[device_id] = now_ts
                else:
                    log("[poll] restore 去重：短时间内已上报，跳过")
        stop_event.wait(POLL_INTERVAL_SECONDS)


def main() -> None:
    session = requests.Session()
    stop_event = threading.Event()

    log("simulate_pi 启动（无限循环；Ctrl+C 退出）")
    log(f"后端地址: {BASE_URL} | 主循环间隔: {LOOP_INTERVAL_SECONDS}s | 轮询间隔: {POLL_INTERVAL_SECONDS}s")

    poll_thread = threading.Thread(target=poll_worker, args=(stop_event,), daemon=True)
    poll_thread.start()

    loop_count = 0
    try:
        while True:
            try:
                loop_count += 1
                selected_device = random.choice(DEVICE_IDS)
                log(
                    f"========== 主循环 loop_count={loop_count} | 设备={selected_device} =========="
                )

                if loop_count == 14:
                    log(
                        "决策: 强制触发 shutdown（loop_count==14，忽略随机概率），将上报并微信推送"
                    )
                    post_event(
                        session,
                        selected_device,
                        "shutdown",
                        force_note="[强制]",
                    )
                else:
                    r = random.random()
                    if r < PROB_SHUTDOWN:
                        log(
                            f"决策: 随机 shutdown（r={r:.6f} < {PROB_SHUTDOWN}），上报并微信推送"
                        )
                        post_event(session, selected_device, "shutdown")
                    elif r < PROB_RESTORE:
                        log(
                            f"决策: 随机 restore（{PROB_SHUTDOWN}<= r={r:.6f} < {PROB_RESTORE}），仅上报"
                        )
                        post_event(session, selected_device, "restore")
                    elif r < PROB_CHECK:
                        log(
                            f"决策: 随机 check（{PROB_RESTORE}<= r={r:.6f} < {PROB_CHECK}），仅上报"
                        )
                        post_event(session, selected_device, "check")
                    else:
                        log(
                            f"决策: 无事件（r={r:.6f} >= {PROB_CHECK}，约 95% 区间），跳过上报"
                        )

                log(f"休眠 {LOOP_INTERVAL_SECONDS}s 后进入下一轮…")
                time.sleep(LOOP_INTERVAL_SECONDS)
            except Exception as exc:
                notify_exception_log(f"主循环 loop_count={loop_count}", exc)
                time.sleep(min(LOOP_INTERVAL_SECONDS, 30.0))
    except KeyboardInterrupt:
        print()
        log("收到 Ctrl+C，正在停止 simulate_pi …")
    finally:
        stop_event.set()
        poll_thread.join(timeout=3)
        log("simulate_pi 已退出")


if __name__ == "__main__":
    main()
