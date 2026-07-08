from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project_model import Project
from app.schemas.project import ProjectCreate
from app.utils.pagination import paginate
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_id(self, project_id: UUID) -> Project | None:
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.tasks),
                selectinload(Project.timesheets),
            )
        )
        return await self.session.scalar(stmt)

    async def get_by_name(self, name: str) -> Project | None:
        stmt = select(Project).where(
            func.lower(Project.name) == name.lower()
        )
        return await self.session.scalar(stmt)

    async def get_by_code(self, code: str) -> Project | None:
        stmt = select(Project).where(
            func.lower(Project.code) == code.lower()
        )
        return await self.session.scalar(stmt)

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: str | None = None,
        manager_id: UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        stmt = select(Project)

        if search:
            query = f"%{search.lower()}%"
            stmt = stmt.where(
                func.lower(Project.name).like(query)
            )

        if status:
            stmt = stmt.where(Project.status == status)

        if manager_id:
            stmt = stmt.where(Project.manager_id == manager_id)

        sort_mapping = {
            "created_at": Project.created_at,
            "updated_at": Project.updated_at,
            "name": Project.name,
            "code": Project.code,
        }

        order_column = sort_mapping.get(
            sort_by,
            Project.created_at,
        )

        stmt = stmt.order_by(
            order_column.desc()
            if sort_order == "desc"
            else order_column.asc()
        )

        return await paginate(
            session=self.session,
            statement=stmt,
            page=page,
            page_size=page_size,
        )

    async def create(
        self,
        payload: ProjectCreate,
        created_by: UUID | None = None,
    ) -> Project:

        project = Project(
            name=payload.name,
            code=payload.code,
            description=payload.description,
            status=payload.status,
            manager_id=payload.manager_id,
            created_by=created_by,
            updated_by=created_by,
        )

        self.session.add(project)

        await self.session.flush()
        await self.session.refresh(project)

        return project

    async def update(
        self,
        project: Project,
        **kwargs,
    ) -> Project:

        for key, value in kwargs.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)

        await self.session.flush()
        await self.session.refresh(project)

        return project

    async def delete(
        self,
        project: Project,
    ) -> None:

        await self.session.delete(project)
        await self.session.flush()

    async def exists_name(
        self,
        name: str,
    ) -> bool:

        stmt = (
            select(func.count())
            .select_from(Project)
            .where(
                func.lower(Project.name) == name.lower()
            )
        )

        return (await self.session.scalar(stmt)) > 0

    async def exists_code(
        self,
        code: str,
    ) -> bool:

        stmt = (
            select(func.count())
            .select_from(Project)
            .where(
                func.lower(Project.code) == code.lower()
            )
        )

        return (await self.session.scalar(stmt)) > 0