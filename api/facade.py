"""API 门面（Facade）：测试只见 api.httpbin.xxx（Law of Demeter）。

端点组合/编排逻辑收敛于此；新增业务域时加一个属性即可（OCP）。
"""

from api.client import ApiClient
from api.endpoints.httpbin import HttpbinEndpoints


class ApiFacade:
    def __init__(self, client: ApiClient) -> None:
        self._client = client
        self.httpbin = HttpbinEndpoints(client)

    def close(self) -> None:
        self._client.close()
