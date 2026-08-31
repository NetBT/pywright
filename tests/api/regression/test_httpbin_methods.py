"""API 回归：HTTP 方法遍历 + 回显校验（完整功能回归，非每次合入必跑）。"""

import pytest


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.parametrize("method", ["get", "post", "put", "delete", "patch"])
def test_http_methods_roundtrip(api, method):
    """/anything 按方法回显：验证请求方法/请求体完整送达。"""
    response = api.httpbin.raw(method.upper(), "/anything", json={"k": "v"})
    assert response.status_code == 200
    body = response.json()
    assert body["method"] == method.upper()
    assert body["json"] == {"k": "v"}
