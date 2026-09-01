"""真实系统接入点示例：占位环境自动 skip，配置 ui_login_enabled 后生效。"""

import pytest


@pytest.mark.regression
@pytest.mark.ui
def test_login_with_real_credentials(app, settings):
    """UI 登录冒烟：真实系统接入后（.env.{env} 开启 ui_login）执行真实凭据登录。"""
    if not settings.auth.ui_login_enabled:
        pytest.skip("占位环境未启用 UI 登录；接入真实系统后在 .env.{env} 开启 TEST_AUTH__UI_LOGIN_ENABLED")
    app.login_page.open().login_as(settings.auth.username, settings.auth.password)
    # 真实系统接入后补充登录成功断言（如首页关键元素可见）
