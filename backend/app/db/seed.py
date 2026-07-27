import asyncio
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal as async_session
from app.db.init_db import init_db
from app.models.user_model import User
from app.models.role_model import Role
from app.models.department_model import Department
from app.models.project_model import Project, ProjectPriority, ProjectStatus
from app.models.project_member_model import ProjectMember
from app.models.task_model import Task
from app.models.subtask_model import SubTask
from app.core.security import hash_password

REQUIRED_EXECUTION_EMP_IDS = {
    "project_manager": "EMP000004",
    "team_lead": "EMP000005",
    "developer": "EMP000006",
    "tester": "EMP000007",
    "business_analyst": "EMP000008",
}


async def _load_seed_users(session):
    emp_ids = set(REQUIRED_EXECUTION_EMP_IDS.values())
    result = await session.execute(
        select(User).where(User.emp_id.in_(emp_ids))
    )
    users_by_emp_id = {
        user.emp_id: user
        for user in result.scalars().all()
    }

    missing_emp_ids = sorted(emp_ids - set(users_by_emp_id))
    if missing_emp_ids:
        print(
            "Skipping project execution seed data. Missing users: "
            f"{', '.join(missing_emp_ids)}"
        )
        return None

    return users_by_emp_id


async def _get_or_create_project(session, project_data, users_by_emp_id):
    existing_project = await session.scalar(
        select(Project).where(Project.code == project_data["code"])
    )
    if existing_project:
        print(f"Project {project_data['code']} already exists. Skipping.")
        return existing_project

    name_conflict = await session.scalar(
        select(Project).where(Project.name == project_data["name"])
    )
    if name_conflict:
        print(
            "Skipping project execution seed project "
            f"{project_data['code']}. Name already exists."
        )
        return None

    manager = users_by_emp_id[project_data["manager_emp_id"]]
    project = Project(
        id=uuid.uuid4(),
        name=project_data["name"],
        code=project_data["code"],
        description=project_data["description"],
        start_date=project_data["start_date"],
        end_date=project_data["end_date"],
        status=project_data["status"],
        priority=project_data["priority"],
        budget=project_data["budget"],
        manager_id=manager.id,
        created_by=manager.id,
        updated_by=manager.id,
        is_deleted=False,
    )

    session.add(project)
    await session.flush()
    print(f"Created project {project.code}.")
    return project


async def _get_or_create_task(session, task_data, project, created_by):
    existing_task = await session.scalar(
        select(Task).where(
            Task.project_id == project.id,
            Task.title == task_data["title"],
        )
    )
    if existing_task:
        print(
            f"Task {task_data['title']} already exists in {project.code}. "
            "Skipping."
        )
        return existing_task

    task = Task(
        id=uuid.uuid4(),
        project_id=project.id,
        title=task_data["title"],
        description=task_data["description"],
        estimated_hours=task_data["estimated_hours"],
        priority=task_data["priority"],
        status=task_data["status"],
        created_by=created_by,
        updated_by=created_by,
        is_deleted=False,
    )

    session.add(task)
    await session.flush()
    print(f"Created task {task.title}.")
    return task


async def _get_or_create_project_member(session, project, user, created_by):
    existing_member = await session.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id,
        )
    )
    if existing_member:
        return existing_member

    member = ProjectMember(
        id=uuid.uuid4(),
        project_id=project.id,
        user_id=user.id,
        created_by=created_by,
        updated_by=created_by,
        is_deleted=False,
    )

    session.add(member)
    await session.flush()
    return member


async def _get_or_create_subtask(
    session,
    subtask_data,
    task,
    users_by_emp_id,
    created_by,
):
    existing_subtask = await session.scalar(
        select(SubTask).where(
            SubTask.task_id == task.id,
            SubTask.title == subtask_data["title"],
        )
    )
    if existing_subtask:
        print(
            f"Subtask {subtask_data['title']} already exists under "
            f"{task.title}. Skipping."
        )
        return existing_subtask

    manager = users_by_emp_id[subtask_data["manager_emp_id"]]
    employee = users_by_emp_id[subtask_data["employee_emp_id"]]
    subtask = SubTask(
        id=uuid.uuid4(),
        task_id=task.id,
        manager_id=manager.id,
        employee_id=employee.id,
        title=subtask_data["title"],
        description=subtask_data["description"],
        estimated_hours=subtask_data["estimated_hours"],
        actual_hours=subtask_data["actual_hours"],
        priority=subtask_data["priority"],
        status=subtask_data["status"],
        start_date=subtask_data["start_date"],
        due_date=subtask_data["due_date"],
        remarks=subtask_data["remarks"],
        created_by=created_by,
        updated_by=created_by,
        is_deleted=False,
    )

    session.add(subtask)
    await session.flush()
    print(f"Created subtask {subtask.title}.")
    return subtask


async def seed_project_execution_data(session):
    print("\n--- Seeding CRUD-Ready Project Execution Data ---")

    users_by_emp_id = await _load_seed_users(session)
    if not users_by_emp_id:
        return

    project_manager = users_by_emp_id[
        REQUIRED_EXECUTION_EMP_IDS["project_manager"]
    ]
    team_lead = users_by_emp_id[
        REQUIRED_EXECUTION_EMP_IDS["team_lead"]
    ]

    projects = [
        {
            "code": "FS-PORTAL-DEMO",
            "name": "FlowSphere Delivery Portal Demo",
            "description": "Seed project for testing project, task, and subtask CRUD flows.",
            "start_date": date(2026, 7, 1),
            "end_date": date(2026, 9, 30),
            "status": ProjectStatus.IN_PROGRESS,
            "priority": ProjectPriority.HIGH,
            "budget": 125000.0,
            "manager_emp_id": project_manager.emp_id,
            "members": [
                "EMP000004",
                "EMP000005",
                "EMP000006",
                "EMP000007",
                "EMP000008",
            ],
            "tasks": [
                {
                    "title": "Requirements Baseline",
                    "description": "Validate workflow assumptions before delivery buildout.",
                    "estimated_hours": 24.0,
                    "priority": "High",
                    "status": "In Progress",
                    "subtasks": [
                        {
                            "title": "Gather stakeholder workflow notes",
                            "description": "Capture expected CRUD paths and approval touchpoints.",
                            "estimated_hours": 8.0,
                            "actual_hours": 2.0,
                            "priority": "High",
                            "status": "In Progress",
                            "start_date": date(2026, 7, 20),
                            "due_date": date(2026, 7, 24),
                            "remarks": "Seeded for Business Analyst subtask testing.",
                            "manager_emp_id": team_lead.emp_id,
                            "employee_emp_id": "EMP000008",
                        },
                    ],
                },
                {
                    "title": "API Foundation",
                    "description": "Prepare backend API endpoints for project execution workflows.",
                    "estimated_hours": 40.0,
                    "priority": "Critical",
                    "status": "In Progress",
                    "subtasks": [
                        {
                            "title": "Build project and task API smoke data",
                            "description": "Exercise linked project and task records through the API.",
                            "estimated_hours": 12.0,
                            "actual_hours": 4.0,
                            "priority": "Critical",
                            "status": "In Progress",
                            "start_date": date(2026, 7, 21),
                            "due_date": date(2026, 7, 28),
                            "remarks": "Seeded for Developer subtask testing.",
                            "manager_emp_id": team_lead.emp_id,
                            "employee_emp_id": "EMP000006",
                        },
                        {
                            "title": "Validate authorization checks",
                            "description": "Confirm project, task, and subtask permissions are available.",
                            "estimated_hours": 10.0,
                            "actual_hours": 0.0,
                            "priority": "High",
                            "status": "Pending",
                            "start_date": date(2026, 7, 22),
                            "due_date": date(2026, 7, 29),
                            "remarks": "Seeded for permission-aware CRUD testing.",
                            "manager_emp_id": team_lead.emp_id,
                            "employee_emp_id": "EMP000006",
                        },
                    ],
                },
                {
                    "title": "QA Regression Pack",
                    "description": "Prepare reusable regression cases for CRUD-ready models.",
                    "estimated_hours": 18.0,
                    "priority": "Medium",
                    "status": "Pending",
                    "subtasks": [
                        {
                            "title": "Prepare CRUD regression scenarios",
                            "description": "Document view, update, and delete checks for seeded records.",
                            "estimated_hours": 8.0,
                            "actual_hours": 1.0,
                            "priority": "Medium",
                            "status": "Pending",
                            "start_date": date(2026, 7, 23),
                            "due_date": date(2026, 7, 31),
                            "remarks": "Seeded for Tester subtask testing.",
                            "manager_emp_id": team_lead.emp_id,
                            "employee_emp_id": "EMP000007",
                        },
                    ],
                },
            ],
        },
        {
            "code": "FS-UTIL-DEMO",
            "name": "Resource Utilization Analytics Demo",
            "description": "Seed project for testing planning and analytics data dependencies.",
            "start_date": date(2026, 8, 1),
            "end_date": date(2026, 10, 15),
            "status": ProjectStatus.PLANNING,
            "priority": ProjectPriority.MEDIUM,
            "budget": 85000.0,
            "manager_emp_id": project_manager.emp_id,
            "members": [
                "EMP000004",
                "EMP000005",
                "EMP000006",
                "EMP000008",
            ],
            "tasks": [
                {
                    "title": "Utilization Metrics Model",
                    "description": "Define metrics needed for resource utilization reporting.",
                    "estimated_hours": 30.0,
                    "priority": "High",
                    "status": "Pending",
                    "subtasks": [
                        {
                            "title": "Define utilization summary calculations",
                            "description": "Map utilization inputs to reporting outputs.",
                            "estimated_hours": 10.0,
                            "actual_hours": 0.0,
                            "priority": "High",
                            "status": "Pending",
                            "start_date": date(2026, 8, 3),
                            "due_date": date(2026, 8, 10),
                            "remarks": "Seeded for Business Analyst planning tests.",
                            "manager_emp_id": project_manager.emp_id,
                            "employee_emp_id": "EMP000008",
                        },
                    ],
                },
                {
                    "title": "Dashboard Drilldowns",
                    "description": "Prepare drilldown tasks for utilization dashboards.",
                    "estimated_hours": 32.0,
                    "priority": "Medium",
                    "status": "Pending",
                    "subtasks": [
                        {
                            "title": "Implement dashboard query fixtures",
                            "description": "Create linked data for dashboard query validation.",
                            "estimated_hours": 14.0,
                            "actual_hours": 0.0,
                            "priority": "Medium",
                            "status": "Pending",
                            "start_date": date(2026, 8, 5),
                            "due_date": date(2026, 8, 14),
                            "remarks": "Seeded for Developer planning tests.",
                            "manager_emp_id": team_lead.emp_id,
                            "employee_emp_id": "EMP000006",
                        },
                    ],
                },
            ],
        },
    ]

    for project_data in projects:
        project = await _get_or_create_project(
            session,
            project_data,
            users_by_emp_id,
        )
        if not project:
            continue

        for emp_id in project_data["members"]:
            await _get_or_create_project_member(
                session,
                project,
                users_by_emp_id[emp_id],
                project_manager.id,
            )

        for task_data in project_data["tasks"]:
            task = await _get_or_create_task(
                session,
                task_data,
                project,
                project_manager.id,
            )
            for subtask_data in task_data["subtasks"]:
                await _get_or_create_subtask(
                    session,
                    subtask_data,
                    task,
                    users_by_emp_id,
                    project_manager.id,
                )

    await session.commit()
    print("CRUD-ready project execution data seeding complete.")

async def run_seed():
    async with async_session() as session:
        # 1. Run the base system initialization
        await init_db(session)
        print("\n--- Seeding Advanced Hierarchical RBAC Test Data ---")
        
        # 2. Seed Test Departments
        departments = [
            {"code": "EXEC", "name": "Executive Management", "description": "C-Suite"},
            {"code": "ENG", "name": "Engineering", "description": "Software Development & QA"}
        ]

        dept_ids = {}
        for dept_data in departments:
            stmt = insert(Department).values(
                id=uuid.uuid4(), code=dept_data["code"], 
                name=dept_data["name"], description=dept_data["description"]
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=['code'],
                set_=dict(name=stmt.excluded.name, description=stmt.excluded.description)
            ).returning(Department.id)
            dept_ids[dept_data["code"]] = await session.scalar(stmt)
        
        await session.commit()

        # 3. Seed Test Users Top-Down
        roles_result = await session.execute(select(Role))
        roles_map = {role.name: role for role in roles_result.scalars().all()}

        # Ordered strictly top-down and using the valid numerical formatting
        test_users = [
            {"emp_id": "EMP000002", "email": "ceo@company.com", "name": "Alice CEO", "roles": ["CEO"], "dept": "EXEC", "mgr_emp_id": None},
            {"emp_id": "EMP000003", "email": "hod@company.com", "name": "Bob HOD", "roles": ["HOD", "Admin"], "dept": "ENG", "mgr_emp_id": "EMP000002"},
            {"emp_id": "EMP000004", "email": "pm@company.com", "name": "Charlie PM", "roles": ["Project Manager"], "dept": "ENG", "mgr_emp_id": "EMP000003"},
            {"emp_id": "EMP000005", "email": "tl@company.com", "name": "Diana TeamLead", "roles": ["Team Lead", "Developer"], "dept": "ENG", "mgr_emp_id": "EMP000004"},
            {"emp_id": "EMP000006", "email": "dev@company.com", "name": "Evan Dev", "roles": ["Developer"], "dept": "ENG", "mgr_emp_id": "EMP000005"},
            {"emp_id": "EMP000007", "email": "qa@company.com", "name": "Fiona QA", "roles": ["Tester"], "dept": "ENG", "mgr_emp_id": "EMP000005"},
            {"emp_id": "EMP000008", "email": "ba@company.com", "name": "George BA", "roles": ["Business Analyst"], "dept": "ENG", "mgr_emp_id": "EMP000005"}
        ]

        default_pwd = await hash_password("Password@123!")
        
        # Cache created users to easily assign reporting_manager_id
        user_id_cache = {}

        for u_data in test_users:
            stmt = select(User).where(User.emp_id == u_data["emp_id"]).options(selectinload(User.roles))
            existing_user = (await session.execute(stmt)).scalar_one_or_none()
            
            if existing_user:
                print(f"Test user {u_data['emp_id']} already exists. Updating roles and cache.")
                existing_user.roles = []
                for role_name in u_data.get("roles", []):
                    role = roles_map.get(role_name)
                    if role:
                        existing_user.roles.append(role)
                await session.commit()
                user_id_cache[u_data["emp_id"]] = existing_user.id
                continue

            # Resolve Manager ID
            mgr_id = user_id_cache.get(u_data["mgr_emp_id"]) if u_data["mgr_emp_id"] else None

            new_user = User(
                id=uuid.uuid4(), emp_id=u_data["emp_id"], email=u_data["email"],
                full_name=u_data["name"], phone_number="5550000000",
                hashed_password=default_pwd, is_active=True, is_first_login=False,
                department_id=dept_ids[u_data["dept"]],
                reporting_manager_id=mgr_id
            )
            
            for role_name in u_data.get("roles", []):
                role = roles_map.get(role_name)
                if role:
                    new_user.roles.append(role)
            
            session.add(new_user)
            await session.commit() 
            await session.refresh(new_user) 
            
            user_id_cache[u_data["emp_id"]] = new_user.id
            print(f"Created {u_data['name']} ({u_data['emp_id']}, {u_data.get('roles')}) -> Reports to: {u_data['mgr_emp_id'] or 'Board'}")
        
        print("Hierarchical RBAC Test Data Seeding Complete.")

        await seed_project_execution_data(session)

if __name__ == "__main__":
    asyncio.run(run_seed())
