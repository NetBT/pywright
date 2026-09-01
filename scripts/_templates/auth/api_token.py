"""策略 1：API token 直用（占位默认，开箱可跑，零浏览器开销）。"""

import logging

from auth.base import AuthResult, BrowserFactory

log = logging.getLogger(__name__)


class ApiTokenStrategy:
    def authenticate(self, settings, env_name: str, browser_factory: BrowserFactory) -> AuthResult:
        log.debug("api_token 策略：使用配置注入的 token（值不外显）")
        return AuthResult(token=settings.auth.token)
