"""AuthManager：按配置选择认证策略（Strategy 选择器，工厂方法轻量形态）。

新认证方式 = 新增策略类 + 在 _resolve 加一个分支（match 穷举，漏配即报错）。
"""

import logging

from auth.api_token import ApiTokenStrategy
from auth.base import AuthResult, AuthStrategy, BrowserFactory
from auth.reuse import ReuseStrategy
from auth.ui_login import UiLoginStrategy
from config.settings import Settings

log = logging.getLogger(__name__)


class AuthManager:
    def __init__(self, settings: Settings, env_name: str) -> None:
        self._settings = settings
        self._env_name = env_name

    def _resolve(self) -> AuthStrategy:
        match self._settings.auth.mode:
            case "api_token":
                return ApiTokenStrategy()
            case "ui_login":
                return UiLoginStrategy()
            case "reuse":
                return ReuseStrategy()
        raise ValueError(f"未知认证模式: {self._settings.auth.mode}")

    def authenticate(self, browser_factory: BrowserFactory) -> AuthResult:
        strategy = self._resolve()
        log.info("认证策略: %s", type(strategy).__name__)
        return strategy.authenticate(self._settings, self._env_name, browser_factory)
