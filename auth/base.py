"""认证策略抽象（Strategy 模式，DIP：AuthManager 依赖 Protocol 而非具体实现）。

认证模式是真实的多分支变化轴（token / UI 登录 / 复用登录态），
新增认证方式 = 新增一个策略类，AuthManager 零改动（OCP）。
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from playwright.sync_api import Browser

    from config.settings import Settings

# 惰性浏览器工厂：仅 UI 登录策略触发浏览器启动（轻量 Proxy/惰性求值）
BrowserFactory = Callable[[], "Browser"]


@dataclass(frozen=True)
class AuthResult:
    """认证产出：token（API 用）与/或 storage_state 路径（UI 用）。"""

    token: str | None = None
    storage_state_path: Path | None = None


class AuthStrategy(Protocol):
    def authenticate(
        self,
        settings: "Settings",
        env_name: str,
        browser_factory: BrowserFactory,
    ) -> AuthResult: ...
