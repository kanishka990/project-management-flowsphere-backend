from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project_member_model import ProjectMember
from app.models.project_model import Project
from app.repositories.base_repository import BaseRepository
from app.schemas.project_schema import ProjectCreate
from app.utils.pagination import paginate

from app.models.task_model import Task
from app.models.subtask_model import SubTask
from app.models.task_assignment_model import TaskAssignment


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
                selectinload(Project.project_members).selectinload(
                    ProjectMember.user
                ),
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
        priority: str | None = None,
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

        if priority:
            stmt = stmt.where(Project.priority == priority)

        if manager_id:
            stmt = stmt.where(Project.manager_id == manager_id)

        sort_mapping = {
            "created_at": Project.created_at,
            "updated_at": Project.updated_at,
            "name": Project.name,
            "code": Project.code,
            "start_date": Project.start_date,
            "end_date": Project.end_date,
            "budget": Project.budget,
            "priority": Project.priority,
            "status": Project.status,
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
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=payload.status,
            priority=payload.priority,
            budget=payload.budget,
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

    async def assign_members(
        self,
        project_id: UUID,
        user_ids: list[UUID],
        created_by: UUID | None = None,
    ) -> list[ProjectMember]:

        for user_id in user_ids:
            stmt = select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )

            existing = await self.session.scalar(stmt)

            if existing:
                continue

            member = ProjectMember(
                project_id=project_id,
                user_id=user_id,
                created_by=created_by,
                updated_by=created_by,
            )

            self.session.add(member)

        await self.session.flush()

        if not user_ids:
            return []

        stmt = (
            select(ProjectMember)
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id.in_(user_ids),
            )
            .options(
                selectinload(ProjectMember.user),
            )
        )

        result = await self.session.scalars(stmt)
        members_by_user_id = {
            member.user_id: member
            for member in result.all()
        }

        return [
            members_by_user_id[user_id]
            for user_id in user_ids
            if user_id in members_by_user_id
        ]

    async def get_project_members(
        self,
        project_id: UUID,
    ) -> list[ProjectMember]:

        stmt = (
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .options(
                selectinload(ProjectMember.user),
            )
        )

        result = await self.session.scalars(stmt)
        return result.all()

    async def remove_member(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> None:

        stmt = delete(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )

        await self.session.execute(stmt)
        await self.session.flush()
        

        async def get_projects_by_user(
            self,
            user_id: UUID,
        ) -> list[dict]:

            stmt = (
                select(Project)
                .join(ProjectMember)
                .where(ProjectMember.user_id == user_id)
                .options(
                    selectinload(Project.manager),
                    selectinload(Project.tasks)
                    .selectinload(Task.assignments),
                    selectinload(Project.tasks)
                    .selectinload(Task.subtasks),
                )
            )

            result = await self.session.scalars(stmt)
            projects = result.unique().all()

            response = []

            for project in projects:
                tasks = []
                subtasks = []

                for task in project.tasks:

                    assigned = any(
                        assignment.user_id == user_id
                        for assignment in task.assignments
                    )

                    if not assigned:
                        continue

                    tasks.append(
                        {
                            "id": task.id,
                            "title": task.title,
                        }
                    )

                    for subtask in task.subtasks:
                        subtasks.append(
                            {
                                "id": subtask.id,
                                "title": subtask.title,
                            }
                        )

                response.append(
                    {
                        "project_id": project.id,
                        "project_name": project.name,
                        "description": project.description,
                        "status": project.status,
                        "priority": project.priority,
                        "start_date": project.start_date,
                        "end_date": project.end_date,
                        "manager_id": project.manager_id,
                        "manager_name": project.manager_name,
                        "tasks": tasks,
                        "subtasks": subtasks,
                        "created_at": project.created_at,
                        "updated_at": project.updated_at,
                    }
                )

            return response