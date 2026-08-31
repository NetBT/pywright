"""POM 基类：URL 路由 + 加载断言骨架（Template Method 轻量形态——仅导航一个模板方法）。

复杂业务流程不强行模板化（改为组合/显式调用），避免"为了模板而模板"。
"""

import logging
from typing import TypeVar

from playwright.sync_api import Page, expect

log = logging.getLogger(__name__)

SelfPage = TypeVar("SelfPage", bound="BasePage")


class BasePage:
    """页面对象基类：path 相对路由，open() 拼接 base_url 导航并等待加载。"""

    path: str = ""

    def __init__(self, page: Page, base_url: str = "") -> None:
        self.page = page
        self._base_url = base_url

    def open(self: SelfPage) -> SelfPage:
        """Template Method：goto → expect_loaded（子类覆写加载断言）。"""
        url = f"{self._base_url}{self.path}"
        log.debug("打开页面: %s", url)
        self.page.goto(url, wait_until="domcontentloaded")
        self.expect_loaded()
        return self

    def expect_loaded(self) -> None:
        """子类覆写：断言页面关键元素可见（auto-waiting 语义）。"""
        raise NotImplementedError

    def expect_title(self, title: str) -> None:
        expect(self.page).to_have_title(title)
