"""UI 回归：筛选/清除等完整功能链路。"""

import pytest


@pytest.mark.regression
@pytest.mark.ui
def test_filter_and_clear(app):
    page = app.todo_page.open().add("A").add("B").complete("A")
    page.filter("completed")
    assert page.items() == ["A"]
    page.filter("all").clear_completed()
    assert page.items() == ["B"]
