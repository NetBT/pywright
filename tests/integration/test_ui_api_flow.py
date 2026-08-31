"""集成测试：API 生成数据 → UI 消费 → 交叉验证（跨层组合场景）。"""

import pytest


@pytest.mark.integration
def test_api_generated_id_flows_into_ui(app, api):
    """API 生成唯一数据，UI 写入并展示，API 侧交叉验证同一数据。"""
    todo_text = f"it-{api.httpbin.uuid()[:8]}"
    app.todo_page.open().add(todo_text)
    assert app.todo_page.items() == [todo_text]
    response = api.httpbin.anything(todo=todo_text)
    assert response.status_code == 200
    assert response.json()["args"]["todo"] == todo_text
