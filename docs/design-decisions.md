# 设计决策记录（ADR 风格）

每个决策含 no-pattern 基线对比：模式是工具不是目的，仅当收益超过其引入的间接层时才采用。

## Design Notes

- **Components**：配置层 / 认证层 / UI 层（页面对象）/ API 层（客户端+端点）/ 数据层 / 测试编排层（fixtures+markers）/ 报告与 CI
- **Patterns chosen**：POM、门面+惰性页面工厂、Facade+Adapter、Strategy、Builder+Director、Template Method（轻量）、"不可变共享实例"替代单例、Agentic Loop（planner/generator/healer）
- **Principles applied**：SRP（每层单一职责）、OCP（新页面/端点/认证方式=新增文件不改旧代码）、DIP（测试依赖抽象，具体实现被 POM/Facade 屏蔽）、LoD（测试只见门面）
- **Alternatives considered**：见下表各决策的 no-pattern 基线
- **Trade-offs**：一层对象化开销换定位符收敛；Protocol 抽象换认证可扩展性；均以"第二个变化轴出现时才引入"为原则

## 决策清单

### 1. POM（Page Object Model）— `pages/`

- **no-pattern 基线**：测试内裸写 `page.locator(".new-todo")`——定位符散落各测试，UI 改版时改动面=全部测试
- **决策**：采用。定位符收敛于页面类（SRP），新页面=新文件（OCP）
- **取舍**：一层对象化开销；换取单点修改与可读的业务语义 API

### 2. Application 门面 + 惰性页面工厂 — `pages/application.py`

- **no-pattern 基线**：测试内散落 `TodoPage(page)` 构造
- **决策**：采用**轻量形态**——`cached_property` 惰性属性即工厂（LoD：测试只见门面）
- **明确拒绝**：registry 版工厂（`register("todo", TodoPage)`）——页面 <20 个时注册表纯增间接层
- **重做触发条件**：页面超 20 个且需插件式装载

### 3. Facade + Adapter（API 层）— `api/client.py` + `api/facade.py`

- **no-pattern 基线**：测试内 `requests.get(f"{base}/users")`——URL 拼接、超时、认证头每处重复；换 HTTP 库=全量改动
- **决策**：ApiClient 对 httpx 做 Adapter（超时/Bearer 头/401 钩子收敛），ApiFacade 组合端点
- **DIP**：测试依赖 ApiClient 抽象——换 HTTP 库只改 client.py 一处
- **选型**：httpx（原生 base_url 合并、默认超时、为 async 留门）；requests 亦可，Facade 隔离下对测试无影响

### 4. Strategy（认证层）— `auth/`

- **no-pattern 基线**：`if mode == "api": ... elif mode == "ui": ...` 散布各 fixture
- **决策**：AuthStrategy Protocol + 3 实现（api_token / ui_login / reuse），AuthManager 按配置选择
- **DIP/OCP**：新认证方式=新类，Manager 零改动（match 穷举，漏配即报错）
- **惰性浏览器**：browser_factory 传 `request.getfixturevalue("browser")` 的 lambda——仅 ui_login 策略才真正启动浏览器，api_token 模式纯 API 测试零浏览器开销

### 5. Builder + Director（数据层）— `test_data/builders/user_builder.py`

- **no-pattern 基线**：dict 字面量拼 payload——无类型、默认值各写各的
- **决策**：**有条件采用**——仅多可选字段/随机派生的聚合对象；2-3 字段静态数据直接用 yaml loader（警戒线："Builder for objects with 2–3 fields" 是反模式）
- **敏感值**：密码/token 只用环境变量 `TEST_*__*` 覆盖（本地 shell 或 CI masked variables），绝不写 env 文件/yaml/代码/git

### 6. Template Method（轻量）— `pages/base_page.py`

- **决策**：仅导航骨架（`open()` → `expect_loaded()`）一个模板方法；复杂业务流程不强行模板化（改用组合/显式调用）

### 7. "不可变共享实例"替代单例 — `config/settings.py`

- **no-pattern 基线（拒绝）**：`__new__` 经典单例——全局可变状态、难测试（首要反模式）
- **决策**：`frozen=True` + `@cache` + session fixture——pytest fixture 作用域本身即 DI 容器，session 级 = 进程内单例，无需任何单例代码
- **结构/值分离**：`config/settings.py` 只放配置结构；值在根目录单一 `.env`（占位值入库）。**环境命名权归用户**：默认环境读 `.env`；自定义环境 = 用户自建 `.env.{自定义名}`（如 `.env.uat`）并 `--env uat` 指定，文件不存在明确报错（防止误用占位配置）

### 8. 明确不用的模式

| 模式 | 不用的理由 |
| --- | --- |
| Abstract Factory | 只有一个具体产品族——塌缩为直接构造 |
| Observer | pytest hooks 已承担事件分发 |
| 自建浏览器工厂 | pytest-playwright 的 browser fixture 本身就是工厂（--browser/--channel/--device 驱动），自建=重复造轮子 |
| Service Locator / IoC 库 | fixture 即 DI 容器 |
| 装饰器栈重试 | 重试由声明式插件（pytest-rerunfailures）承担 |

### 9. AI 协作测试（Playwright 官方 Agent 能力）— `specs/` + `tests/`

- **no-pattern 基线**：AI 直接在测试文件内“边看边改”，缺少计划与边界，容易生成脆弱定位符、重复逻辑、跨层耦合
- **决策**：采用 Playwright 官方 Agentic Loop 思路（planner / generator / healer），但加人工审阅闸门
- **落地约定**：
  - planner 产物放 `specs/`（人类可读、可审阅的测试计划）
  - generator 产物放 `tests/`（可执行用例）
  - healer 仅提交修复建议，合并前必须人工 review + 回归验证
- **边界约束**：AI 生成代码必须回收进既有分层（POM / Facade / fixtures），禁止把定位符与业务细节散落在测试脚本
- **取舍**：增加一次审阅成本，换取更快的用例扩展速度与更低的长期维护成本

### 10. AI 浏览器交互通道选型（MCP vs CLI）

- **no-pattern 基线**：统一走一种交互通道，导致要么上下文开销大（复杂快照），要么能力不足（复杂探索）
- **决策**：双通道并存，按场景选择
  - MCP：用于探索式、多步推理场景（基于 accessibility tree 的结构化交互）
  - playwright-cli：用于 token 敏感、命令式、短链路操作
- **安全约束**：`browser_run_code_unsafe` 属于 RCE 等价能力，仅对受信任客户端启用
- **取舍**：增加工具选择复杂度，换取效率与可观测性的平衡

## 关键机制决策

### 默认执行策略（`tests/conftest.py`）

`pytest_configure` 中未显式 `-m` 时设置 markexpr：裸跑 `pytest` = `smoke and not wip`；`--wip` = `wip`。显式 `-m` 优先级最高。

### 失败重试三层分工

1. Playwright auto-waiting：始终开启，这是正确等待语义而非重试
2. `expect().to_pass()`：断言级竞态
3. pytest-rerunfailures：只作用于 `@flaky(reruns=N)` 标记 + CI 回归 stage `--reruns 2`；CI job 级 retry 只挂 `runner_system_failure` 等基础设施失败

**禁用全局盲目 rerun**——掩盖真实缺陷、拖慢流水线。不用 Playwright JS 运行器的 `retries`（pytest 生态不可用）。

### 失败产物归档（`utils/allure_attach.py`）

- `--screenshot=only-on-failure --tracing=retain-on-failure`：仅失败用例落盘
- hook 时机：`makereport(call)` 失败打标记（item.stash），`makereport(teardown)` 产物完整（trace 在 context 关闭时落盘）后挂 allure 附件
- 产物目录匹配：pytest-playwright 把 nodeid 非字母数字替换为 `-`、参数化 `]` 删除；`_safe_nodeid` 复刻该规则（验证阶段已用失败用例核对）

### 日志（`utils/logger.py`）

dictConfig 双通道：FileHandler(DEBUG) → `artifacts/logs/run_{ts}.log`；StreamHandler(WARNING) 保终端干净。SecretsFilter 先格式化再脱敏（教训：先清 args 会丢参数）。`browser.console` 独立 logger 承接 `page.on("console")`。

### 环境配置

覆盖顺序：环境变量 `TEST_*__*` → env 文件（`--env default` 读 `.env`，自定义环境读 `.env.{自定义名}`）→ 代码默认值。占位值入库保证开箱即用；真实敏感值只走环境变量/CI masked variables。

### AI 协作执行规范

1. 先规划后生成：优先由 planner 输出可审阅计划，再由 generator 生成测试代码。
2. 失败定位优先级：UI Mode / Trace Viewer > 盲目加等待或全局重试。
3. 稳定性红线：继续遵循“用户可见行为断言 + resilient locators + 禁止全局盲目 rerun”。
