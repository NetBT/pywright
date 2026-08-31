"""日志配置：双通道（DEBUG 落文件 / WARNING 上终端）+ 敏感信息脱敏。

pytest 会捕获 stdout/stderr，测试失败时才回显终端输出，因此终端通道只保留
WARNING+ 避免刷屏；细节一律看 artifacts/logs/run_*.log 或 Allure 报告附件。
"""

import logging
import re
from datetime import datetime
from logging.config import dictConfig
from pathlib import Path

LOG_DIR = Path("artifacts") / "logs"


class SecretsFilter(logging.Filter):
    """脱敏 password/token/authorization/secret 等敏感字段（保留键名）。"""

    _PATTERNS = (re.compile(r"(password|token|authorization|secret)([=:]\s*)\S+", re.IGNORECASE),)

    def filter(self, record: logging.LogRecord) -> bool:
        # 先应用 args 格式化（否则参数丢失），再对完整消息脱敏
        record.msg = record.getMessage()
        record.args = ()
        for pattern in self._PATTERNS:
            record.msg = pattern.sub(lambda m: f"{m.group(1)}{m.group(2)}***", record.msg)
        return True


def setup_logging() -> None:
    """dictConfig 双通道：FileHandler(DEBUG) + StreamHandler(WARNING)。"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"secrets": {"()": SecretsFilter}},
            "formatters": {
                "default": {"format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"},
            },
            "handlers": {
                "file": {
                    "class": "logging.FileHandler",
                    "filename": str(LOG_DIR / f"run_{timestamp}.log"),
                    "encoding": "utf-8",
                    "formatter": "default",
                    "filters": ["secrets"],
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "WARNING",
                    "formatter": "default",
                    "filters": ["secrets"],
                },
            },
            "root": {"level": "DEBUG", "handlers": ["file", "console"]},
        }
    )
