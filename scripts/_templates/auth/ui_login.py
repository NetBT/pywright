"""策略 2：UI 登录获取会话，storage_state 落盘供后续复用。

占位环境（login_url 未配置）抛出带接入指引的错误；接入真实系统时：
① .env.{env} 配置 TEST_AUTH__LOGIN_URL / UI_LOGIN_ENABLED / USERNAME / PASSWORD
② 实现 pages/login_page.py 的定位符与登录流程。
"""

import logging
from pathlib import Path

from auth.base import AuthResult, BrowserFactory

log = logging.getLogger(__name__)

AUTH_STATE_DIR = Path("artifacts") / "auth_state"


class UiLoginStrategy:
    def authenticate(self, settings, env_name: str, browser_factory: BrowserFactory) -> AuthResult:
        if not settings.auth.login_url or not settings.auth.ui_login_enabled:
            raise NotImplementedError(
                "UI 登录策略需要真实系统接入：在 .env.{env} 配置 TEST_AUTH__LOGIN_URL 与 "
                "TEST_AUTH__UI_LOGIN_ENABLED=true，并实现 pages/login_page.py 的登录流程。"
            )
        browser = browser_factory()
        context = browser.new_context()
        try:
            page = context.new_page()
            page.goto(settings.auth.login_url)
            from pages.login_page import LoginPage

            LoginPage(page).login_as(settings.auth.username, settings.auth.password)
            AUTH_STATE_DIR.mkdir(parents=True, exist_ok=True)
            state_path = AUTH_STATE_DIR / f"{env_name}.json"
            context.storage_state(path=str(state_path))
            log.info("UI 登录完成，登录态已保存: %s", state_path)
        finally:
            context.close()
        return AuthResult(storage_state_path=state_path)
