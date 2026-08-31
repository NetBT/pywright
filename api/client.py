"""httpx 适配层（Adapter）：超时、认证头、401 钩子收敛于此。

测试只依赖 ApiClient 抽象（DIP）——换 HTTP 库（如 requests）只改本文件，
测试与 Facade 零改动。不自动 raise_for_status：负面场景（断言 4xx）控制权留给测试。
"""

import logging
from collections.abc import Callable
from typing import Any

import httpx

log = logging.getLogger(__name__)


class ApiClient:
    """对 httpx.Client 的 Adapter：base_url 合并、默认超时、Bearer 认证头、401 钩子。"""

    def __init__(self, base_url: str, *, token: str | None = None, timeout_ms: int = 10_000) -> None:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        self._client = httpx.Client(base_url=base_url, headers=headers, timeout=timeout_ms / 1000)
        # 401 时重新获取 token 的钩子（真实系统接入时实现：刷新 token 后重放请求）
        self._on_401: Callable[[], str | None] | None = None

    def set_401_handler(self, handler: Callable[[], str | None]) -> None:
        self._on_401 = handler

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        response = self._client.request(method, path, **kwargs)
        if response.status_code == 401 and self._on_401 is not None:
            token = self._on_401()
            if token:
                self._client.headers["Authorization"] = f"Bearer {token}"
                log.info("401 后已刷新 token 并重放请求")
                return self._client.request(method, path, **kwargs)
        return response

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("DELETE", path, **kwargs)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
