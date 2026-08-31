"""静态测试数据加载：环境无关、无敏感信息的数据放 test_data/fixtures/*.yaml。

敏感值（密码/token）一律用环境变量 TEST_*__* 覆盖（本地 shell 或 CI masked variables），绝不进 yaml/env 文件/代码/git。
"""

from pathlib import Path
from typing import Any

import yaml

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_yaml(name: str) -> dict[str, Any]:
    """加载 test_data/fixtures/{name}.yaml。"""
    path = FIXTURES_DIR / f"{name}.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)
