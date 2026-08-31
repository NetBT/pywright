"""API 冒烟：连通性与认证链路（每次合入必跑，失败即阻断）。"""

import pytest


@pytest.mark.smoke
@pytest.mark.api
def test_api_connectivity(api):
    """配置驱动的 api_base_url 真实生效（httpbin 回显断言）。"""
    response = api.httpbin.anything(ping="1")
    assert response.status_code == 200
    assert response.json()["args"]["ping"] == "1"


@pytest.mark.smoke
@pytest.mark.api
def test_bearer_auth(api, settings):
    """认证链路：Bearer 头真实送达（httpbin /bearer 校验认证结果）。"""
    assert settings.auth.mode == "api_token"
    body = api.httpbin.bearer().json()
    assert body["authenticated"] is True
