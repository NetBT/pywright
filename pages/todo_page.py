"""TodoMVC 占位示例页：展示 POM 规范（定位符收敛 + 链式操作）。"""

from playwright.sync_api import expect

from pages.base_page import BasePage


class TodoPage(BasePage):
    """TodoMVC demo 页面对象。"""

    path = "/"

    # --- 定位符（唯一改动点：UI 改版只改这里） ---
    NEW_TODO = ".new-todo"
    ITEMS = "ul.todo-list li"
    COMPLETED_ITEMS = "ul.todo-list li.completed"
    TOGGLE = ".toggle"
    CLEAR_COMPLETED = "button.clear-completed"
    FILTERS = "ul.filters li a"

    def expect_loaded(self) -> None:
        expect(self.page.locator(self.NEW_TODO)).to_be_visible()

    # --- 行为 ---
    def add(self, text: str) -> "TodoPage":
        box = self.page.locator(self.NEW_TODO)
        box.fill(text)
        box.press("Enter")
        return self

    def items(self) -> list[str]:
        return self.page.locator(self.ITEMS).all_text_contents()

    def complete(self, text: str) -> "TodoPage":
        item = self.page.locator(self.ITEMS).filter(has_text=text)
        item.locator(self.TOGGLE).check()
        return self

    def completed_count(self) -> int:
        return self.page.locator(self.COMPLETED_ITEMS).count()

    def filter(self, name: str) -> "TodoPage":
        """name: all | active | completed（"all" 筛选器 href 为 "#/"）。"""
        href = "#/" if name == "all" else f"#/{name}"
        self.page.locator(f'{self.FILTERS}[href="{href}"]').click()
        return self

    def clear_completed(self) -> "TodoPage":
        self.page.locator(self.CLEAR_COMPLETED).click()
        return self
