from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _generate_next_code(self, model: type, prefix: str) -> str:
        """
        Generates the next sequential code safely within a transaction block.
        """
        stmt = (
            select(model.emp_id)
            .where(model.emp_id.like(f"{prefix}%"))
            .order_by(model.emp_id.desc())
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