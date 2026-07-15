from uuid import UUID
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.department_model import Department
from app.repositories.base_repository import BaseRepository
from app.schemas.department_schema import DepartmentCreate
from app.utils.pagination import paginate

class DepartmentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        
    async def get_by_id(self, dept_id: UUID) -> Department | None:
        stmt = select(Department).where(Department.id == dept_id)
        return await self.session.scalar(stmt)
        
    async def get_by_code(self, code: str) -> Department | None:
        stmt = select(Department).where(func.lower(Department.code) == code.lower())
        return await self.session.scalar(stmt)

    async def get_by_name(self, name: str) -> Department | None:
        stmt = select(Department).where(func.lower(Department.name) == name.lower())
        return await self.session.scalar(stmt)
        
    async def list(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ):
        stmt = select(Department)
        
        if search:
            query_expr = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Department.name).like(query_expr),
                    func.lower(Department.code).like(query_expr),
                )
            )
            
        sort_mapping = {
            "name": Department.name,
            "code": Department.code,
        }
        stmt = self._apply_sorting(stmt, Department, sort_by, sort_order, sort_mapping)
        
        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size
        )

    async def create(self, payload: DepartmentCreate) -> Department:
        dept = Department(
            name=payload.name,
            code=payload.code,
            description=payload.description,
        )
        self.session.add(dept)
        await self.session.flush()
        await self.session.refresh(dept)
        return dept
        
    async def update(self, dept: Department, **kwargs) -> Department:
        for key, value in kwargs.items():
            if hasattr(dept, key) and value is not None:
                setattr(dept, key, value)
        await self.session.flush()
        await self.session.refresh(dept)
        return dept
        
    async def delete(self, dept: Department) -> None:
        await self.session.delete(dept)
        await self.session.flush()


