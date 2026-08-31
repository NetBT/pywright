"""UI 层专属 fixture：浏览器控制台日志转发。

共享门面 app 与登录态注入（browser_context_args 覆写）已收敛于根 conftest。
"""

import logging

import pytest

log = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def _forward_browser_console(page):
    """浏览器 console 转发到 browser.console logger（error 级别上浮为 ERROR）。"""

    def on_console(msg) -> None:
        level = logging.ERROR if msg.type == "error" else logging.DEBUG
        logging.getLogger("browser.console").log(level, "[%s] %s", msg.type, msg.text)

    page.on("console", on_console)
    yield
