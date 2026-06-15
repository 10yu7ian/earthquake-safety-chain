import os

from sct_api import post_sct_send

SEND_KEY = os.getenv("SERVERCHAN_KEY")

if not SEND_KEY:
    print("警告: 环境变量 SERVERCHAN_KEY 未设置，无法发送推送")
else:
    try:
        r = post_sct_send(
            SEND_KEY,
            "【地震安链】测试消息",
            "这是一条测试推送，如果你收到说明 SendKey 可用。",
        )
        print("状态码:", r.status_code)
        print("响应:", r.text)
    except Exception as e:
        print("发送失败:", e)
        print(
            "排查：本客户端默认不使用系统代理（避免错误代理导致 SSL 握手失败）。"
            "若必须通过代理上网，请设置环境变量 SCT_USE_SYSTEM_PROXY=1。"
        )
        print(
            "仍报证书相关错误时，可尝试：pip install -U certifi urllib3 requests；"
            "或在确认存在 HTTPS 解密代理时临时设置 SCT_VERIFY_SSL=0。"
        )
