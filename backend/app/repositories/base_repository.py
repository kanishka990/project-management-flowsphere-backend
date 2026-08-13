from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _generate_next_code(self, model: type, field_name: str, prefix: str) -> str:
        column_attr = getattr(model, field_name)
        stmt = (
            select(column_attr)
            .where(column_attr.like(f"{prefix}%"))
            .order_by(column_attr.desc())
            .with_for_update()
            .limit(1)
        )
        last_code = await self.session.scalar(stmt)
        if last_code:
            last_number = int(last_code.replace(prefix, ""))
            next_number = last_number + 1
        else:
            next_number = 1
        return f"{prefix}{next_number:06d}"

    async def soft_delete(self, entity, user_id: str | None = None) -> None:
        """
        Soft deletes an entity if it supports FullAuditMixin.
        """
        from datetime import datetime, UTC
        if hasattr(entity, "is_deleted"):
            entity.is_deleted = True
            entity.deleted_at = datetime.now(UTC)
            if hasattr(entity, "deleted_by") and user_id:
                entity.deleted_by = user_id
            await self.session.flush()

    def _apply_sorting(self, stmt, model, sort_by: str, sort_order: str, sort_mapping: dict | None = None):
        """
        Applies sorting to a SQLAlchemy statement.
        """
        sort_mapping = sort_mapping or {}
        order_column = sort_mapping.get(sort_by, getattr(model, "created_at", None))
        
        if order_column is None:
            # Fallback to id if created_at doesn't exist
            order_column = getattr(model, "id")
            
        return stmt.order_by(order_column.desc() if sort_order == "desc" else order_column.asc())