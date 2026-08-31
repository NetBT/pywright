"""根 conftest：全局选项、配置注入、默认执行策略、产物/日志集成（Composition Root）。

- --env: 选择根目录 .env.{env} 配置文件（默认 dev）
- --wip: 只跑 wip 用例；默认裸跑 pytest = 只跑 smoke 且排除 wip
- 显式 -m 优先级最高（尊重调用方意图）

fixture 即 DI 容器：session 级 settings 由 get_settings 提供进程内唯一不可变实例
（frozen + lru_cache，替代经典单例，见 docs/design-decisions.md）。
跨层共享 fixture（settings/env_name/auth_state/api/app/browser_context_args）收敛于此；
层专属 fixture 留在各层 conftest（如 tests/ui/conftest.py 的控制台转发）。
"""

import logging
import shutil

import pytest

from config.settings import Settings, get_settings
from utils.allure_attach import ALLURE_RESULTS_DIR, attach_failure_artifacts, write_allure_environment
from utils.logger import setup_logging

log = logging.getLogger(__name__)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--env",
        action="store",
        default="default",
        metavar="NAME",
        help="测试环境：default 读根目录 .env；自定义环境读 .env.NAME（需自建该文件）",
    )
    parser.addoption(
        "--wip",
        action="store_true",
        help="只运行 wip 标记用例（默认排除 wip）",
    )


def pytest_configure(config: pytest.Config) -> None:
    setup_logging()
    # 默认执行策略：未显式指定 -m 时，--wip 只跑 wip；否则只跑 smoke（排除 wip）
    if not config.option.markexpr:
        config.option.markexpr = "wip" if config.getoption("--wip") else "smoke and not wip"
    log.info("默认执行策略: -m %s", config.option.markexpr)


@pytest.fixture(scope="session")
def env_name(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def settings(request: pytest.FixtureRequest) -> Settings:
    return get_settings(request.config.getoption("--env"))


@pytest.fixture(scope="session")
def auth_state(settings: Settings, env_name: str, request: pytest.FixtureRequest):
    """会话级认证结果。

    浏览器通过 browser_factory 惰性获取（request.getfixturevalue），
    仅 ui_login 策略需要时才会真正启动浏览器；api_token 模式下纯 API 测试零浏览器开销。
    """
    from auth.manager import AuthManager

    manager = AuthManager(settings, env_name)
    return manager.authenticate(browser_factory=lambda: request.getfixturevalue("browser"))


# --- 跨层共享门面（API 层/UI 层/集成测试共用） ---


@pytest.fixture(scope="session")
def api(settings: Settings, auth_state):
    """API 门面：session 级复用连接池；仅在被请求时实例化。"""
    from api.client import ApiClient
    from api.facade import ApiFacade

    client = ApiClient(
        str(settings.app.api_base_url),
        token=auth_state.token,
        timeout_ms=settings.browser.default_timeout_ms,
    )
    yield ApiFacade(client)
    client.close()


@pytest.fixture
def app(page, settings: Settings):
    """UI 门面：function 级随 page 生命周期（测试隔离的 context 保证状态干净）。"""
    from pages.application import Application

    return Application(page, str(settings.app.ui_base_url))


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, auth_state):
    """注入登录态（pytest-playwright 官方推荐覆写点，session 级）。"""
    if auth_state.storage_state_path:
        browser_context_args["storage_state"] = str(auth_state.storage_state_path)
    return browser_context_args


@pytest.fixture(scope="session", autouse=True)
def _allure_environment(settings: Settings, env_name: str):
    """session 开始清空 allure 结果目录（防多次运行混杂）并写入环境信息。"""
    if ALLURE_RESULTS_DIR.exists():
        shutil.rmtree(ALLURE_RESULTS_DIR)
    write_allure_environment(env_name, settings)
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """call 失败打标记；teardown 报告阶段产物（trace 在 context 关闭时落盘）已完整，再挂 allure 附件。"""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        item.stash["_failed_call"] = True
    elif report.when == "teardown" and item.stash.get("_failed_call", False):
        attach_failure_artifacts(item)
