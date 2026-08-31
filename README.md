# pywright

Pytest + Playwright 分层测试框架：**UI 测试**（POM）、**API 测试**（httpx Facade）、**冒烟/回归/集成**分层、多环境配置、Allure 报告、GitLab CI。

设计模式与取舍记录见 [docs/design-decisions.md](docs/design-decisions.md)。

## 快速开始

### 环境依赖

1. [uv](https://docs.astral.sh/uv/getting-started/installation/) + [Python3](https://docs.astral.sh/uv/guides/install-python/)
2. [Playwright](https://playwright.dev/python/docs/library)
3. [Node.js](https://nodejs.org/) + [Allure Report](https://allurereport.org/docs/v3/install/)

### 新项目初始化（脚手架）

```shell
# 一次性安装（uv tool 自动管理运行环境；团队分发可改用 git 仓库 URL）
uv tool install git+https://github.com/NetBT/pywright

# 之后任意目录：
pywright /work/new-project                        # 最简：占位配置，跑通后改 .env
pywright /work/new-project --name new_project --ui-url https://app.example.com --api-url https://api.example.com   # 指定项目名与占位地址
pywright /work/new-project --install --git        # 全自动：生成 + uv sync + 装 chromium + git init
pywright /work/new-project --dry-run              # 预览文件清单（不写盘）
```

| 参数                     | 说明                                   | 默认值              |
| ------------------------ | -------------------------------------- | ------------------- |
| `target`                 | 目标项目目录（位置参数，必填）         | —                   |
| `--name`                 | 项目名（写入 pyproject.toml）          | 目标目录名          |
| `--ui-url` / `--api-url` | 占位地址（写入 .env）                  | TodoMVC / httpbin   |
| `--auth-mode`            | 认证模式（写入 .env）                  | `api_token`         |
| `--token`                | 占位 token（真实值用环境变量覆盖）     | `placeholder-token` |
| `--git`                  | 生成后 `git init`                      | 关闭                |
| `--install`              | 生成后 `uv sync` + 安装 chromium       | 关闭                |
| `--force`                | 目标目录非空时仍继续（不删除现有文件） | 关闭                |
| `--dry-run`              | 只打印文件清单，不写盘                 | 关闭                |

脚本为纯标准库实现（Python 3.12+ 即可运行，无需本项目依赖）。

### 安装依赖 (--install 后可略过)

```shell
# 1. 安装依赖（uv 自动创建 .venv 与 Python 3.12）
uv sync --all-groups

# 2. 安装浏览器
uv run playwright install chromium

# 3. 运行冒烟（裸跑 pytest 默认即冒烟；默认环境读根目录 .env）
uv run pytest
uv run pytest -m smoke

# 回归 / 集成
uv run pytest -m regression
uv run pytest -m integration

# 自定义环境：复制 .env 为 .env.uat 并按需修改，--env 指定环境名
uv run pytest -m smoke --env uat

# 只看进行中的用例
uv run pytest --wip
```

## 目录结构

```text
├── pyproject.toml        # 依赖 + pytest 配置 + markers 注册 + ruff
├── .env                  # 默认环境占位配置（入库，开箱即用；自定义环境自建 .env.{自定义名}）
├── .gitlab-ci.yml        # lint → smoke → regression → report
├── config/settings.py    # pydantic-settings 配置模型（结构，不含值）
├── pages/                # UI 层：BasePage / 页面对象 / Application 门面
├── api/                  # API 层：ApiClient(Adapter) / ApiFacade / Endpoints
├── auth/                 # 认证策略层：api_token / ui_login / reuse
├── test_data/            # 数据层：yaml 静态数据 + Builder/Director
├── utils/                # 日志（双通道+脱敏）/ Allure 辅助
├── artifacts/            # 运行时产物（截图/trace/日志/allure 结果，gitignore）
└── tests/
    ├── conftest.py       # 根：--env/--wip、默认策略、跨层共享 fixture、失败附件 hook
    ├── api/              # API 测试（smoke/regression 子目录）
    ├── ui/               # UI 测试（smoke/regression 子目录）
    └── integration/      # UI+API 跨层组合
```

## 测试类型（markers）

| Marker               | 用途                               | 默认执行时机               |
| -------------------- | ---------------------------------- | -------------------------- |
| `smoke`              | 关键路径，失败即阻断               | 裸跑 `pytest` 默认只跑冒烟 |
| `regression`         | 完整功能回归                       | `-m regression`            |
| `integration`        | UI+API 跨层场景                    | `-m integration`           |
| `ui` / `api`         | 层标签（与上三个 marker 组合使用） | —                          |
| `wip`                | 进行中，默认排除                   | `--wip` 时只跑 wip         |
| `flaky(reruns: int)` | 已知不稳定，登记技术债             | 需 `--reruns N`            |

显式 `-m` 优先级最高（覆盖默认策略）。

## 环境配置

**环境命名权归用户**——框架不预置任何环境名，只内置一个默认环境：

- 默认环境：根目录 `.env`（占位值入库，开箱即用），`--env default`（默认值，可省略）。
- 自定义环境：复制 `.env` 为 `.env.{自定义名}`（如 `.env.uat`、`.env.test01`）并按需修改，运行 `--env uat` 指定。文件不存在会**明确报错**（防止误用占位配置）。
- 覆盖顺序：环境变量 `TEST_*__*` → env 文件 → 代码默认值。
- **真实敏感值**（token/密码）不写入 env 文件——用环境变量 `TEST_*__*` 覆盖（本地 shell 或 CI masked variables）。

## Allure 报告

```shell
# 结果自动生成于 artifacts/allure-results（session 开始自动清空防混杂）
allure generate artifacts/allure-results -o artifacts/allure-report --clean
allure open artifacts/allure-report
```

- 失败用例自动附加：截图（png）、trace（zip，可 `playwright show-trace` 回放）、浏览器 console 日志。
- 报告页 Environment 展示运行环境信息（env/URL/认证模式/Python 版本）。

## 接入真实系统（只改配置 + 两处实现）

1. 改根目录 `.env`：
   - `TEST_APP__UI_BASE_URL` / `TEST_APP__API_BASE_URL` → 真实地址
   - `TEST_AUTH__MODE` / `TEST_AUTH__TOKEN` → 认证方式（真实敏感值用环境变量 `TEST_*__*` 覆盖，勿写入 .env）
2. 实现对应页面对象：仿照 `pages/todo_page.py` 新建页面类（定位符收敛），注册到 `pages/application.py` 门面；真实 UI 登录需实现 `pages/login_page.py` 并在 .env 开启 `TEST_AUTH__UI_LOGIN_ENABLED`。
3. 实现对应 API 端点类：仿照 `api/endpoints/httpbin.py`，注册到 `api/facade.py`。

测试、fixture、CI 零改动。

## GitLab CI

流水线 `lint → smoke → regression → report`：

- `smoke`（默认环境）每次 MR/合入必跑；多环境扩展见 .gitlab-ci.yml 内注释示例（自定义 job 名与 `TEST_ENV`，对应自建的 `.env.{env}` 文件）
- `regression` 依赖冒烟通过，带 `--reruns 2` 容忍已标记 flaky 用例
- `report` 聚合 Allure 结果生成静态报告（启用 GitLab Pages 后取消 .gitlab-ci.yml 末尾注释即可发布）

## 代码质量

```shell
uv run ruff check .
uv run ruff format --check .
```

失败重试三层分工：① Playwright auto-waiting（始终开启，正确等待语义）；② `expect().to_pass()` 处理断言级竞态；③ `--reruns` 只作用于 `@flaky` 标记与 CI 回归 stage——**禁止全局盲目重试**（掩盖真实缺陷）。
