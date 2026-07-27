import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user_model import User
from app.models.role_model import Role
from app.models.permission_model import Permission
from app.models.menu_model import Menu
from app.models.submenu_model import SubMenu
from app.models.department_model import Department
from app.core.security import hash_password

# --- CATALOG DEFINITION ---
MENUS = [
    {
        "code": "setup",
        "name": "Setup & Configuration",
        "path": None,
        "icon": "settings",
        "sort_order": 10,
        "submenus": [
            {
                "code": "user_mgt",
                "title": "User Management",
                "path": "/setup/users",
                "icon": "users",
                "sort_order": 10,
                "permissions": [
                    "users:create",
                    "users:read",
                    "users:update",
                    "users:delete",
                ],
            },
            {
                "code": "role_mgt",
                "title": "Role Management",
                "path": "/setup/roles",
                "icon": "shield",
                "sort_order": 20,
                "permissions": [
                    "roles:create",
                    "roles:read",
                    "roles:update",
                    "roles:delete",
                ],
            },
            {
                "code": "perm_mgt",
                "title": "Permission Management",
                "path": "/setup/permissions",
                "icon": "key-round",
                "sort_order": 30,
                "permissions": [
                    "permissions:create",
                    "permissions:read",
                    "permissions:update",
                    "permissions:delete",
                ],
            },
            {
                "code": "menu_mgt",
                "title": "Menu Management",
                "path": "/setup/menus",
                "icon": "panel-left",
                "sort_order": 40,
                "permissions": [
                    "menus:create",
                    "menus:read",
                    "menus:update",
                    "menus:delete",
                    "submenus:create",
                    "submenus:read",
                    "submenus:update",
                    "submenus:delete",
                ],
            },
        ],
    },

    {
        "code": "project_mgt",
        "name": "Project Management",
        "path": None,
        "icon": "briefcase",
        "sort_order": 20,
        "submenus": [
            {
                "code": "project_mgt",
                "title": "Projects",
                "path": "/projects",
                "icon": "folder-kanban",
                "sort_order": 10,
                "permissions": [
                    "projects:create",
                    "projects:read",
                    "projects:update",
                    "projects:delete",
                ],
            },
            {
                "code": "task_mgt",
                "title": "Tasks",
                "path": "/tasks",
                "icon": "list-checks",
                "sort_order": 20,
                "permissions": [
                    "tasks:create",
                    "tasks:read",
                    "tasks:update",
                    "tasks:delete",
                    "tasks:assign",
                ],
            },
            {
                "code": "subtask_mgt",
                "title": "SubTasks",
                "path": "/subtasks",
                "icon": "git-branch-plus",
                "sort_order": 30,
                "permissions": [
                    "subtasks:create",
                    "subtasks:read",
                    "subtasks:update",
                    "subtasks:delete",
                ],
            },
            {
                "code": "timesheet_mgt",
                "title": "Timesheets",
                "path": "/timesheets",
                "icon": "clock",
                "sort_order": 40,
                "permissions": [
                    "timesheets:create",
                    "timesheets:read",
                    "timesheets:update",
                    "timesheets:delete",
                    "timesheets:approve",
                    "timesheets:reject",
                ],
            },
        ],
    },
]

DEFAULT_ROLES = [
    {"name": "SuperAdmin", "description": "System owner with absolute access (IT/DevOps)"},
    {"name": "Admin", "description": "System Owner with maximum access"},
    {"name": "CEO", "description": "Executive with global read-only and reporting access"},
    {"name": "HOD", "description": "Department Head managing budgets, teams, and high-level projects"},
    {"name": "Project Manager", "description": "Manages project scope, timelines, and assigns Team Leads"},
    {"name": "Team Lead", "description": "Tactical execution manager and blocker resolution"},
    {"name": "Developer", "description": "Technical execution and task completion"},
    {"name": "Tester", "description": "Quality assurance and bug reporting"},
    {"name": "Business Analyst", "description": "Requirements gathering and backlog management"}
]

CRUD_READY_ROLE_PERMISSIONS = {
    "Project Manager": {
        "users:read",
        "projects:create",
        "projects:read",
        "projects:update",
        "projects:delete",
        "tasks:create",
        "tasks:read",
        "tasks:update",
        "tasks:delete",
        "tasks:assign",
        "subtasks:create",
        "subtasks:read",
        "subtasks:update",
        "subtasks:delete",
    },
    "Team Lead": {
        "users:read",
        "projects:read",
        "tasks:create",
        "tasks:read",
        "tasks:update",
        "tasks:assign",
        "subtasks:create",
        "subtasks:read",
        "subtasks:update",
        "subtasks:delete",
    },
    "Developer": {
        "projects:read",
        "tasks:read",
        "subtasks:read",
        "subtasks:update",
    },
    "Tester": {
        "projects:read",
        "tasks:read",
        "subtasks:read",
        "subtasks:update",
    },
    "Business Analyst": {
        "projects:read",
        "tasks:read",
        "subtasks:read",
        "subtasks:update",
    },
}

async def init_db(session: AsyncSession):
    print("Starting Database Initialization...")

    # 0. UPSERT DEFAULT DEPARTMENT
    dept_stmt = insert(Department).values(
        id=uuid.uuid4(), code="SYSADMIN", name="System Administration", description="Default department"
    )
    dept_stmt = dept_stmt.on_conflict_do_update(
        index_elements=['code'], set_=dict(name=dept_stmt.excluded.name)
    ).returning(Department.id)
    sys_dept_id = await session.scalar(dept_stmt)

    # 1. UPSERT MENUS & SUBMENUS & PERMISSIONS
    for m_data in MENUS:
        stmt = insert(Menu).values(
            id=uuid.uuid4(),
            code=m_data["code"],
            name=m_data["name"],
            path=m_data.get("path"),
            icon=m_data.get("icon"),
            sort_order=m_data.get("sort_order", 0),
            is_active=True,
            is_deleted=False,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['code'],
            set_=dict(
                name=stmt.excluded.name,
                path=stmt.excluded.path,
                icon=stmt.excluded.icon,
                sort_order=stmt.excluded.sort_order,
                is_active=stmt.excluded.is_active,
                is_deleted=False,
            )
        ).returning(Menu.id)
        menu_id = await session.scalar(stmt)

        for sub_data in m_data["submenus"]:
            sub_stmt = insert(SubMenu).values(
                id=uuid.uuid4(),
                code=sub_data["code"],
                title=sub_data["title"],
                menu_id=menu_id,
                path=sub_data.get("path"),
                icon=sub_data.get("icon"),
                sort_order=sub_data.get("sort_order", 0),
                is_active=True,
                is_deleted=False,
            )
            sub_stmt = sub_stmt.on_conflict_do_update(
                index_elements=['code'],
                set_=dict(
                    title=sub_stmt.excluded.title,
                    menu_id=sub_stmt.excluded.menu_id,
                    path=sub_stmt.excluded.path,
                    icon=sub_stmt.excluded.icon,
                    sort_order=sub_stmt.excluded.sort_order,
                    is_active=sub_stmt.excluded.is_active,
                    is_deleted=False,
                )
            ).returning(SubMenu.id)
            submenu_id = await session.scalar(sub_stmt)

            for perm_code in sub_data["permissions"]:
                action = perm_code.split(":")[-1]
                p_stmt = insert(Permission).values(
                    id=uuid.uuid4(), code=perm_code, action=action, 
                    description=f"Can {action} {perm_code.split(':')[0]}", submenu_id=submenu_id,
                    is_deleted=False
                )
                p_stmt = p_stmt.on_conflict_do_update(
                    index_elements=['code'],
                    set_=dict(submenu_id=p_stmt.excluded.submenu_id, description=p_stmt.excluded.description)
                )
                await session.execute(p_stmt)

    # 2. UPSERT ROLES
    for r_data in DEFAULT_ROLES:
        r_stmt = insert(Role).values(id=uuid.uuid4(), name=r_data["name"], description=r_data["description"], is_deleted=False)
        r_stmt = r_stmt.on_conflict_do_update(
            index_elements=['name'], set_=dict(description=r_stmt.excluded.description)
        )
        await session.execute(r_stmt)
    
    await session.commit()

    # 3. ASSIGN PERMISSIONS TO ROLES
    all_roles = (await session.scalars(select(Role).options(selectinload(Role.permissions)))).all()
    all_perms = (await session.scalars(select(Permission))).all()
    roles_map = {r.name: r for r in all_roles}

    for role_name, role_obj in roles_map.items():
        current_perm_ids = {p.id for p in role_obj.permissions}
        for perm in all_perms:
            if perm.id in current_perm_ids:
                continue
            
            if role_name == "SuperAdmin":
                role_obj.permissions.append(perm)
            elif role_name == "CEO" and perm.code.endswith(":read"):
                role_obj.permissions.append(perm)
            elif role_name == "HOD" and perm.code.startswith("users:") and not perm.code.endswith(":delete"):
                role_obj.permissions.append(perm)
            elif role_name == "Project Manager" and perm.code == "users:read":
                role_obj.permissions.append(perm)
            elif perm.code in CRUD_READY_ROLE_PERMISSIONS.get(role_name, set()):
                role_obj.permissions.append(perm)
                
    await session.commit()

    # 4. UPSERT DEFAULT SUPERADMIN USER (Using correct format)
    admin_emp_id = "EMP000001"
    stmt = select(User).where(User.emp_id == admin_emp_id).options(selectinload(User.roles))
    admin_user = (await session.execute(stmt)).scalar_one_or_none()

    if not admin_user:
        super_admin_role = roles_map.get("SuperAdmin")
        admin_user = User(
            id=uuid.uuid4(),
            emp_id=admin_emp_id,
            email="admin@company.com",
            full_name="System Administrator",
            phone_number="9876543210",
            hashed_password=await hash_password("Password@123!"),
            is_active=True,
            is_first_login=False,
            department_id=sys_dept_id 
        )
        if super_admin_role:
            admin_user.roles.append(super_admin_role)
        session.add(admin_user)
        await session.commit()
    
    print("Database Initialization Complete.")
