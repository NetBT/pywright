"""Application 门面：测试的 UI 入口（Law of Demeter——测试只见门面，不见 Playwright Page）。

惰性页面工厂（轻量工厂形态）：cached_property 首次访问才构造页面对象。
刻意拒绝 registry 版工厂（register("todo", TodoPage)）——页面 <20 个时注册表纯增间接；
页面超 20 个且需插件式装载时再考虑。
"""

from functools import cached_property

from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.todo_page import TodoPage


class Application:
    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url

    def _build(self, page_cls: type[BasePage]) -> BasePage:
        return page_cls(self._page, self._base_url)

    @cached_property
    def todo_page(self) -> TodoPage:
        return self._build(TodoPage)

    @cached_property
    def login_page(self) -> LoginPage:
        return self._build(LoginPage)
