"""flaky 标记用法示例：已知不稳定的用例打上标记。

- 本地：标记生效需要显式 --reruns（如 pytest -m regression --reruns 2）
- CI：回归 stage 已带 --reruns 2，标记值覆盖全局默认
- 原则：flaky 是技术债登记手段，不是常态——排查根因后应移除标记
"""

import pytest


@pytest.mark.flaky(reruns=2)
@pytest.mark.regression
@pytest.mark.ui
def test_flaky_marked_example(app):
    """稳定用例演示 flaky 标记语法；真实不稳定用例按此模式标记。"""
    app.todo_page.open().add("flaky demo")
    assert app.todo_page.items() == ["flaky demo"]
