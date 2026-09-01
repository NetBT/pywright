"""UI 冒烟：TodoMVC 关键路径（占位站点示例，接入真实系统后以真实页面替换）。"""

import pytest


@pytest.mark.smoke
@pytest.mark.ui
def test_add_todo(app):
    todo = app.todo_page.open()
    todo.add("buy milk")
    assert todo.items() == ["buy milk"]


@pytest.mark.smoke
@pytest.mark.ui
def test_complete_todo(app):
    page = app.todo_page.open().add("task A")
    page.complete("task A")
    assert page.completed_count() == 1
