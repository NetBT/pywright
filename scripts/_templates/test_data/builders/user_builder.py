"""Builder + Director：仅复杂聚合对象用（多可选字段/随机派生）。

2-3 字段的静态数据直接用 test_data/loader.py 的 yaml 加载（Builder 反模式警戒线：
"Builder for objects with 2–3 fields; a plain constructor is clearer"）。
"""

import uuid
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class UserData:
    username: str
    role: str = "standard"
    password: str = "password"
    email: str | None = None


class UserBuilder:
    """逐步构造用户数据；默认用户名随机派生（避免并发/重复注册冲突）。"""

    def __init__(self) -> None:
        self._username = f"user_{uuid.uuid4().hex[:8]}"
        self._role = "standard"
        self._password = "password"
        self._email: str | None = None

    def with_username(self, username: str) -> Self:
        self._username = username
        return self

    def with_role(self, role: str) -> Self:
        self._role = role
        return self

    def with_password(self, password: str) -> Self:
        self._password = password
        return self

    def with_email(self, email: str) -> Self:
        self._email = email
        return self

    def build(self) -> UserData:
        return UserData(username=self._username, role=self._role, password=self._password, email=self._email)


class UserDirector:
    """命名场景一处定义：admin() / standard_user()，测试直接引用。"""

    @staticmethod
    def admin() -> UserData:
        return UserBuilder().with_role("admin").build()

    @staticmethod
    def standard_user() -> UserData:
        return UserBuilder().with_role("standard").build()
