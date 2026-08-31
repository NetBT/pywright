"""真实系统接入点：占位登录页对象。

接入步骤：实现真实登录表单的定位符与 login_as 流程，
然后在 .env.{env} 配置 TEST_AUTH__LOGIN_URL / UI_LOGIN_ENABLED。
"""

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    def expect_loaded(self) -> None:
        # 占位：真实系统接入时断言登录表单元素可见
        raise NotImplementedError("真实系统接入时实现登录页加载断言")

    def login_as(self, username: str, password: str) -> None:
        """填写凭据并提交登录；成功后会话进入 page context（storage_state 由 auth 层保存）。"""
        raise NotImplementedError("真实系统接入时实现本方法：定位用户名/密码输入框，填写并提交登录表单。")
