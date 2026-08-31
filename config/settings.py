"""框架配置模型。

设计说明：
- 结构（本文件）与值（根目录 .env）分离，pydantic-settings 负责加载。
- frozen=True + cache + session fixture = "不可变共享实例"，替代经典单例
  （全局可变状态是测试框架可测试性的大敌，见 docs/design-decisions.md）。
- 覆盖顺序：环境变量 TEST_*__* → env 文件 → 代码默认值。
- 环境命名权归用户：默认环境（--env default）读根目录 .env；
  自定义环境 = 用户自建 .env.{自定义名}（如 .env.uat），--env uat 指定，
  文件不存在时明确报错（防止误用占位配置）。
"""

from functools import cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class AppSettings(BaseModel):
    """被测应用地址。占位值指向公开演示站点，接入真实系统时只改 env 文件。"""

    ui_base_url: str = "https://demo.playwright.dev/todomvc"
    api_base_url: str = "https://httpbin.org"


class AuthSettings(BaseModel):
    """认证配置。mode 决定 AuthManager 选择的策略（Strategy 模式）。

    - api_token: 直接使用 token 调 API（占位默认，开箱可跑）
    - ui_login: 通过 UI 登录页获取会话，保存 storage_state
    - reuse: 复用 artifacts/auth_state/ 下已保存的登录态
    """

    mode: Literal["api_token", "ui_login", "reuse"] = "api_token"
    token: str = "placeholder-token"
    token_url: str = ""
    ui_login_enabled: bool = False
    login_url: str = ""
    username: str = ""
    password: str = ""


class BrowserSettings(BaseModel):
    """浏览器相关配置。browser/channel/device 由 pytest-playwright CLI 选项控制。"""

    default_timeout_ms: int = 10_000


class Settings(BaseSettings):
    """顶层配置。字段对应根目录 .env 文件中的键名（大小写不敏感）。"""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",  # 默认读 .env；get_settings 可切换到 .env.{env}
        env_prefix="TEST_",
        env_nested_delimiter="__",
        extra="ignore",
        frozen=True,
    )

    app: AppSettings = AppSettings()
    auth: AuthSettings = AuthSettings()
    browser: BrowserSettings = BrowserSettings()


@cache
def get_settings(env: str = "default") -> Settings:
    """加载环境配置（进程内缓存一次）。

    默认环境（default）读根目录 .env；自定义环境（用户自定名）读 .env.{env}，
    文件不存在时抛错——静默回退占位配置会误导"跑的是哪个环境"。
    """
    if env == "default":
        return Settings(_env_file=PROJECT_ROOT / ".env")
    env_file = PROJECT_ROOT / f".env.{env}"
    if not env_file.exists():
        raise FileNotFoundError(f"自定义环境配置文件不存在: {env_file}（复制 .env 创建并按需修改）")
    return Settings(_env_file=env_file)
