#!/usr/bin/env python3
"""pywright 框架脚手架：一键把本框架模板初始化到新项目。

用法（在本框架根目录）:
    python scripts/scaffold.py ../my-project
    python scripts/scaffold.py D:/work/my-project --name my_project
    python scripts/scaffold.py ../my-project --ui-url https://app.example.com \\
        --api-url https://api.example.com --auth-mode api_token --install --git
    python scripts/scaffold.py ../my-project --dry-run

设计说明：
- 模板位于 scripts/_templates/，运行时产物与敏感文件绝不复制
- 标准库实现，零额外依赖；生成后自动 uv sync + 浏览器安装（--install）
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

# 绝不复制/覆盖的文件（.env 作为模板一部分正常复制并渲染占位值）
EXCLUDE_FILES: set[str] = set()

NAME_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")

# scaffold.py 自身随模板传播；模板不包含 scripts/。
SCAFFOLD_REL = Path("scripts") / "scaffold.py"


def template_root() -> Path:
    """返回包内唯一的测试项目模板目录。"""
    return Path(__file__).resolve().parent / "_templates"


def _read_template(rel: Path) -> str:
    """读取模板文件；scaffold 自身读当前包代码，其余读模板根。"""
    if rel == SCAFFOLD_REL:
        return Path(__file__).read_text(encoding="utf-8")
    return (template_root() / rel).read_text(encoding="utf-8")


def collect_template_files() -> list[Path]:
    """收集模板根下所有需复制的文件（相对路径）并附加 scaffold 自身。"""
    files = [
        path.relative_to(template_root())
        for path in sorted(template_root().rglob("*"))
        if path.is_file() and path.name not in EXCLUDE_FILES
    ]
    files.append(SCAFFOLD_REL)
    return files


def render_file(rel: Path, text: str, ctx: dict) -> str:
    """按文件类型替换模板占位：pyproject 项目名 / README 标题 / .env 键值。"""
    if rel.name == "pyproject.toml":
        text = re.sub(r'^name = "pywright"', f'name = "{ctx["name"]}"', text, flags=re.M)
    elif rel.name == "README.md":
        text = re.sub(r"^# pywright$", f"# {ctx['name']}", text, flags=re.M)
    elif rel.name == ".env":
        text = render_env_content(text, ctx)
    return text


def render_env_content(text: str, ctx: dict) -> str:
    """注入 URL/认证参数到 .env 配置。"""
    body = re.sub(r"^TEST_APP__UI_BASE_URL=.*$", f"TEST_APP__UI_BASE_URL={ctx['ui_url']}", text, flags=re.M)
    body = re.sub(r"^TEST_APP__API_BASE_URL=.*$", f"TEST_APP__API_BASE_URL={ctx['api_url']}", body, flags=re.M)
    body = re.sub(r"^TEST_AUTH__MODE=.*$", f"TEST_AUTH__MODE={ctx['auth_mode']}", body, flags=re.M)
    body = re.sub(r"^TEST_AUTH__TOKEN=.*$", f"TEST_AUTH__TOKEN={ctx['token']}", body, flags=re.M)
    return body


def find_uv() -> str:
    """定位 uv 可执行文件：PATH 优先，其次官方安装位置（%USERPROFILE%\\.local\\bin）。"""
    if shutil.which("uv"):
        return "uv"
    candidates = [
        Path.home() / ".local" / "bin" / "uv.exe",
        Path.home() / ".local" / "bin" / "uv",
        Path.home() / ".cargo" / "bin" / "uv.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return "uv"  # 找不到时仍返回裸名，让 subprocess 报清晰错误


def run(cmd: list[str], cwd: Path) -> None:
    """执行外部命令，失败即中止（带清晰错误提示）。

    命令列表完全由脚本内部构造（固定参数，无用户输入拼接），无注入面。
    """
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=False)  # noqa: S603
    if result.returncode != 0:
        sys.exit(f"命令失败（exit {result.returncode}）: {' '.join(cmd)}")


def create_project(target: Path, ctx: dict, dry_run: bool) -> list[str]:
    """复制模板 + 渲染，返回已创建文件清单（供 dry-run/摘要共用）。"""
    created: list[str] = []

    def write(rel: Path, content: str) -> None:
        created.append(str(rel))
        if dry_run:
            return
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

    for rel in collect_template_files():
        text = _read_template(rel)
        write(rel, render_file(rel, text, ctx))
    return created


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="pywright 框架脚手架：一键初始化新项目的 pytest+playwright 测试框架",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("target", help="目标项目目录（不存在则创建）")
    parser.add_argument("--name", help="项目名（写入 pyproject.toml；默认取目标目录名）")
    parser.add_argument("--ui-url", default="https://demo.playwright.dev/todomvc", help="UI 占位地址（写入 .env）")
    parser.add_argument("--api-url", default="https://httpbin.org", help="API 占位地址（写入 .env）")
    parser.add_argument("--auth-mode", default="api_token", choices=["api_token", "ui_login", "reuse"], help="认证模式")
    parser.add_argument("--token", default="placeholder-token", help="占位 token（真实值用环境变量 TEST_*__* 覆盖）")
    parser.add_argument("--git", action="store_true", help="生成后 git init")
    parser.add_argument("--install", action="store_true", help="生成后 uv sync + 安装 chromium")
    parser.add_argument("--force", action="store_true", help="目标目录非空时仍继续（不删除现有文件）")
    parser.add_argument("--dry-run", action="store_true", help="只打印将生成的文件清单，不写盘")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    name = args.name or target.name
    if not NAME_PATTERN.fullmatch(name):
        sys.exit(f"非法项目名（需符合 Python 包名规范 [A-Za-z0-9._-]）: {name}")

    if target.exists() and any(target.iterdir()) and not args.force and not args.dry_run:
        sys.exit(f"目标目录非空: {target}（如需继续请加 --force，现有文件不会被删除）")

    print(f"初始化测试框架到: {target}")
    print(f"  项目名={name}  auth={args.auth_mode}  模板来源={template_root()}")
    ctx = {
        "name": name,
        "ui_url": args.ui_url,
        "api_url": args.api_url,
        "auth_mode": args.auth_mode,
        "token": args.token,
    }
    created = create_project(target, ctx, args.dry_run)

    if args.dry_run:
        print(f"\n[dry-run] 将创建 {len(created)} 个文件:")
        for f in created:
            print(f"  {f}")
        return 0

    print(f"已创建 {len(created)} 个文件")

    if args.git:
        run(["git", "init"], target)
    if args.install:
        uv = find_uv()
        run([uv, "sync", "--all-groups"], target)
        run([uv, "run", "playwright", "install", "chromium"], target)

    print(
        f"""
完成。下一步:
  cd {target}
  uv run pytest                       # 冒烟（裸跑默认即冒烟，默认环境读 .env）
  uv run pytest -m regression
  uv run pytest -m integration
  # 自定义环境：复制 .env 为 .env.<自定义名>，--env <自定义名> 运行
"""
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
