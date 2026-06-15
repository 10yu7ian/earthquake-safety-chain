"""访问 Server酱 (sctapi.ftqq.com)：IPv4 优先、默认不走系统代理、可选关闭证书校验。"""
import os
import socket
from typing import Optional

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 遇 SSLEOFError 时，多为 IPv6 路径异常；默认仅解析 IPv4
_FORCE_IPV4 = os.environ.get("SCT_FORCE_IPV4", "1").lower() not in (
    "0",
    "false",
    "no",
)


def prefer_ipv4() -> None:
    if not _FORCE_IPV4:
        return
    try:
        from urllib3.util import connection
    except ImportError:
        return
    connection.allowed_gai_family = lambda: socket.AF_INET


def _ssl_verify_flag() -> bool:
    return os.environ.get("SCT_VERIFY_SSL", "1").lower() not in ("0", "false", "no")


def _use_system_proxy() -> bool:
    return os.environ.get("SCT_USE_SYSTEM_PROXY", "0").lower() in ("1", "true", "yes")


def _sct_session(verify: bool) -> requests.Session:
    prefer_ipv4()
    session = requests.Session()
    # 忽略 HTTP(S)_PROXY，避免错误代理导致 SSLEOF；需代理时设 SCT_USE_SYSTEM_PROXY=1
    session.trust_env = _use_system_proxy()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.4,
        status_forcelist=(502, 503, 504),
        allowed_methods=("POST",),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.verify = verify
    return session


def post_sct_send(
    send_key: str,
    title: str,
    desp: str,
    *,
    timeout: float = 15,
    verify: Optional[bool] = None,
) -> requests.Response:
    if verify is None:
        verify = _ssl_verify_flag()
    if not verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = f"https://sctapi.ftqq.com/{send_key}.send"
    session = _sct_session(verify)
    try:
        return session.post(
            url,
            json={"title": title, "desp": desp},
            timeout=timeout,
        )
    finally:
        session.close()
