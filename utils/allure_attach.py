"""Allure 报告辅助：运行环境信息 + 失败用例产物附件。

失败附件匹配依赖 pytest-playwright 的产物目录命名（nodeid 中非字母数字字符被
替换为 '-'、参数化的 ']' 被删除）；若插件改名规则变化，先跑一个失败用例核对
artifacts/playwright/ 实际目录结构后调整 _safe_nodeid。
"""

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import allure
import pytest

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from config.settings import Settings

ALLURE_RESULTS_DIR = Path("artifacts") / "allure-results"
PLAYWRIGHT_OUTPUT_DIR = Path("artifacts") / "playwright"


def write_allure_environment(env_name: str, settings: "Settings") -> None:
    """把当前运行环境写入 environment.properties（报告页 Overview/Environment 展示）。"""
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    import platform

    lines = [
        f"env={env_name}",
        f"ui_base_url={settings.app.ui_base_url}",
        f"api_base_url={settings.app.api_base_url}",
        f"auth_mode={settings.auth.mode}",
        f"python={platform.python_version()}",
        f"os={platform.system()} {platform.release()}",
    ]
    (ALLURE_RESULTS_DIR / "environment.properties").write_text("\n".join(lines), encoding="utf-8")


def _attach_file(path: Path) -> None:
    """按文件类型挂进 allure：截图 PNG / 视频 WEBM / trace 以 zip 归档。"""
    suffix = path.suffix.lower()
    if suffix == ".png":
        allure.attach.file(path, name="screenshot", attachment_type=allure.attachment_type.PNG)
    elif suffix == ".webm":
        allure.attach.file(path, name="video", attachment_type=allure.attachment_type.WEBM)
    elif suffix == ".zip":  # Playwright trace，以 zip 归档供下载回放
        allure.attach.file(path, name="trace", attachment_type=allure.attachment_type.TEXT, extension="zip")


def _safe_nodeid(nodeid: str) -> str:
    """nodeid → pytest-playwright 产物目录名的 sanitize 规则。

    插件把非字母数字（含下划线）全部替换为 '-'，但参数化的 ']' 被删除而非替换：
    test_xxx[chromium] → test-xxx-chromium（无尾随连字符），故 strip('-') 收尾。
    """
    return re.sub(r"[^A-Za-z0-9]+", "-", nodeid).strip("-")


def attach_failure_artifacts(item: pytest.Item) -> None:
    """失败用例：把 screenshot/trace/video 挂进 allure 步骤附件。

    产物目录位于 playwright 输出根下的一级子目录（目录名 = sanitize 后的 nodeid），
    先匹配目录再收集其中文件（rglob 的 * 不跨目录段，直接对文件匹配会漏）。
    """
    if not PLAYWRIGHT_OUTPUT_DIR.exists():
        return
    safe = _safe_nodeid(item.nodeid)
    files = []
    for d in PLAYWRIGHT_OUTPUT_DIR.iterdir():
        if d.is_dir() and safe in d.name:
            files.extend(f for f in d.iterdir() if f.is_file())
    log.debug("失败附件匹配 nodeid=%s files=%s", item.nodeid, files)
    for path in files:
        _attach_file(path)
