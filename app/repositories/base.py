"""
数据访问基类
提供通用的 CRUD 操作
"""
from typing import TypeVar, Generic, List, Optional, Any, Dict
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.postgresql import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """数据访问基类"""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """根据 ID 获取单条记录"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """获取所有记录"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """根据字段获取单条记录"""
        field = getattr(self.model, field_name)
        result = await self.session.execute(
            select(self.model).where(field == value)
        )
        return result.scalar_one_or_none()

    async def get_by_fields(self, filters: Dict[str, Any]) -> List[ModelType]:
        """根据多个字段获取记录列表"""
        result = await self.session.execute(
            select(self.model).filter_by(**filters)
        )
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """创建记录"""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """更新记录"""
        result = await self.session.execute(
            update(self.model).where(self.model.id == id).values(**data)
        )
        await self.session.flush()
        if result.rowcount > 0:
            return await self.get_by_id(id)
        return None

    async def delete(self, id: int) -> bool:
        """删除记录"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def count(self) -> int:
        """统计记录数"""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0