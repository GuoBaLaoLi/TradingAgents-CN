"""
用户仓库
提供用户数据的 CRUD 操作
"""
import hashlib
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgresql_models import Users
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[Users]):
    """用户仓库"""

    def __init__(self, session: AsyncSession):
        super().__init__(Users, session)

    async def get_by_username(self, username: str) -> Optional[Users]:
        """根据用户名获取用户"""
        result = await self.session.execute(
            select(Users).where(Users.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Users]:
        """根据邮箱获取用户"""
        result = await self.session.execute(
            select(Users).where(Users.email == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    async def authenticate(self, username: str, password: str) -> Optional[Users]:
        """验证用户登录"""
        user = await self.get_by_username(username)
        if not user:
            return None
        password_hash = self._hash_password(password)
        if user.hashed_password == password_hash:
            return user
        return None