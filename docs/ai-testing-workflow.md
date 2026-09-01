# AI 协作测试工作流示范

本项目使用 Playwright 官方的 Agentic Loop 思路：**planner → generator → healer**。AI 用于加速探索、生成和诊断；测试设计、代码合并与缺陷结论仍由人负责。

> 本项目基于 Python + pytest-playwright；Playwright Test Agents 生成的是 JavaScript/TypeScript 用例。将其作为流程与浏览器探索能力使用，最终测试实现必须遵守本项目的 pytest、POM、API Facade 与 fixture 约定。

## 1. 准备：提供可复用的上下文

为每个待覆盖的业务流程准备以下输入：

- 需求或验收标准：描述用户目标、前置条件、成功与失败结果。
- 测试环境：通过根目录 `.env` 或 `.env.{环境名}` 配置地址与认证方式；敏感值只通过环境变量或 CI masked variables 提供。
- 已有测试：优先复用 `tests/` 的 fixture、`pages/` 中的页面对象、`api/` 中的 API Facade。

示例需求：

> 已登录用户创建一个待办事项，刷新页面后该事项仍存在；空白事项不得创建。

## 2. Planner：生成可审阅的测试计划

使用 AI 浏览器探索应用，先生成 Markdown 计划，再审阅后进入代码生成。计划文件应保存在项目根目录 `specs/`，例如 `specs/todo-create.md`；该目录存放真实项目计划，不在本仓库预置示例文件。

计划至少包含：

1. 场景目标与业务风险。
2. 前置条件、测试数据与清理策略。
3. 可观察的步骤和预期结果。
4. 用例分层：`smoke`、`regression` 或 `integration`。
5. 需要 mock 的外部依赖及其契约。

使用 Playwright Test Agents 时，可生成当前编辑器集成的定义：

```shell
npx playwright init-agents --loop=vscode
```

官方 Agent 的 `planner` 会探索应用并输出计划；本项目中应把该输出整理为上述 `specs/` 计划格式，而不是直接把探索结果当作最终测试。

## 3. Generator：从计划生成可维护的 pytest 用例

AI 生成或改写测试时，必须遵循下列映射：

| 关注点 | 本项目位置 | 规则 |
| --- | --- | --- |
| UI 交互与定位符 | `pages/` | 仅在页面对象中维护定位符与操作方法。 |
| UI 测试 | `tests/ui/smoke/`、`tests/ui/regression/` | 测试表达业务意图，不直接写复杂定位符。 |
| API 交互 | `api/` | 通过 `ApiFacade` 与端点类封装请求。 |
| API 测试 | `tests/api/smoke/`、`tests/api/regression/` | 断言接口契约和业务结果。 |
| 跨层流程 | `tests/integration/` | 仅覆盖关键 UI + API 协作路径。 |
| 测试数据 | `test_data/` | 静态数据优先 YAML；复杂对象才用 Builder。 |

针对“创建待办事项”的计划，AI 生成后的代码应呈现为：

```python
@pytest.mark.smoke
@pytest.mark.ui
def test_user_can_create_a_todo(app: Application) -> None:
    app.todo.open()
    app.todo.add_item("Buy groceries")
    app.todo.expect_item_visible("Buy groceries")
```

示例强调边界：测试描述行为，页面对象封装浏览器细节。生成代码后必须人工检查 marker、fixture、断言、数据隔离和敏感信息。

## 4. MCP 与 playwright-cli：探索和验证页面

### MCP：多步探索与结构化页面理解

Playwright MCP 使用 accessibility tree 的角色、名称与元素引用，不依赖视觉识别。适合让 AI：

- 发现用户流程和可访问的交互控件。
- 检查 role、label、text、test id 是否足以形成稳定定位符。
- 验证网络请求、控制台错误或 mock 行为。

启动方式：

```shell
npx @playwright/mcp@latest
```

MCP 默认保持浏览器 profile。验证隔离场景时，使用 `--isolated`，避免继承登录状态或 cookie。`browser_run_code_unsafe` 是 RCE 等价能力，仅应向受信任的本地客户端开放。

### playwright-cli：低上下文开销的短链路操作

对快速复现、冒烟探测或截图取证，优先使用面向编码代理的 CLI：

```shell
npm install -g @playwright/cli@latest
playwright-cli install --skills
playwright-cli open https://demo.playwright.dev/todomvc/ --headed
playwright-cli snapshot
playwright-cli screenshot
```

`playwright-cli` 适合短链路命令式操作；需要持续基于页面结构推理或复杂探索时选择 MCP。

## 5. Healer：以证据驱动修复

失败时不允许 AI 直接增加固定等待或扩大重试。遵守以下顺序：

1. 重跑最小失败用例，确认是否可复现。
2. 查看 Allure 附件中的截图、trace 和浏览器 console 日志。
3. 在 Trace Viewer 中检查动作、DOM 快照、网络请求、报错与源码位置。
4. 使用 UI Mode 或 MCP 复现当前 UI，判断是产品缺陷、测试数据问题、环境问题还是定位符变化。
5. 由 AI 提供最小补丁建议；人工审查后运行相应 smoke/regression 用例。

本项目已通过 pytest-playwright 配置在失败时保留 trace；保持该策略，禁止为了让测试通过而全局开启重试或全量 trace。

## 6. 完成定义（Definition of Done）

每次 AI 参与的测试变更在合并前必须满足：

- 测试计划已审阅，且与验收标准一一对应。
- 新增测试被正确标记为 `smoke`、`regression` 或 `integration`，并附带 `ui` 或 `api` 层标签。
- UI 定位符优先使用面向用户的 role、label、text，或稳定的 test id；避免 CSS/XPath 结构路径。
- 用例可独立执行，不依赖其他用例遗留的 cookie、存储或数据。
- 不提交 token、密码、浏览器 storage state、trace 中的敏感数据或真实用户数据。
- 修改后的最小测试集和相关回归集均通过；AI 自动修复也必须经人工 review。

## 官方资料

- [Playwright Test Agents](https://playwright.dev/docs/test-agents)
- [Playwright MCP](https://playwright.dev/docs/getting-started-mcp)
- [Coding agents / playwright-cli](https://playwright.dev/docs/getting-started-cli)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Trace Viewer](https://playwright.dev/docs/trace-viewer)
