"""策略 3：复用已保存的 storage_state（跳过重复登录，提速本地回归）。"""

import logging
from pathlib import Path

from auth.base import AuthResult, BrowserFactory

log = logging.getLogger(__name__)

AUTH_STATE_DIR = Path("artifacts") / "auth_state"


class ReuseStrategy:
    def authenticate(self, settings, env_name: str, browser_factory: BrowserFactory) -> AuthResult:
        state_path = AUTH_STATE_DIR / f"{env_name}.json"
        if not state_path.exists():
            raise FileNotFoundError(
                f"登录态不存在: {state_path}。先以 auth.mode=ui_login 跑一次生成，或改回 api_token 模式。"
            )
        log.info("复用已保存登录态: %s", state_path)
        return AuthResult(storage_state_path=state_path)
