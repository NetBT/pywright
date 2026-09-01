"""httpbin 占位端点：验证框架真实可跑。

接入真实系统时仿照本文件新建 Endpoint 类（每个业务域一个类，SRP），
并在 ApiFacade 上暴露，测试与 fixture 零改动。
"""

from typing import Any

import httpx

from api.client import ApiClient


class HttpbinEndpoints:
    """httpbin.org 端点集合。"""

    def __init__(self, client: ApiClient) -> None:
        self._client = client

    def anything(self, **params: Any) -> httpx.Response:
        """回显请求内容——断言配置驱动的 base_url 真实生效。"""
        return self._client.get("/anything", params=params)

    def bearer(self) -> httpx.Response:
        """httpbin /bearer 验证 Authorization Bearer 头，返回 {"authenticated": true}。"""
        return self._client.get("/bearer")

    def uuid(self) -> str:
        """生成随机 UUID（供集成测试生成跨层数据）。"""
        response = self._client.get("/uuid")
        return response.json()["uuid"]

    def raw(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """任意方法/路径透传（回归测试遍历 HTTP 方法用）。"""
        return self._client.request(method, path, **kwargs)
