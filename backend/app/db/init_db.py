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
            {
                "code": "department_mgt",
                "title": "Departments",
                "path": "/setup/departments",
                "icon": "building-2",
                "sort_order": 50,
                "permissions": [
                    "departments:create",
                    "departments:read",
                    "departments:update",
                    "departments:delete",
                ],
            },
        ],
    },

    {
        "code": "dashboard",
        "name": "Dashboards",
        "path": None,
        "icon": "layout-dashboard",
        "sort_order": 15,
        "submenus": [
            {
                "code": "employee_dashboard",
                "title": "Employee Dashboard",
                "path": "/dashboard/employee",
                "icon": "user-round-check",
                "sort_order": 10,
                "permissions": [
                    "dashboard:read",
                    "dashboard:employee",
                ],
            },
            {
                "code": "project_dashboard",
                "title": "Project Dashboard",
                "path": "/dashboard/project",
                "icon": "kanban-square",
                "sort_order": 20,
                "permissions": [
                    "dashboard:read",
                    "dashboard:project",
                ],
            },
            {
                "code": "team_dashboard",
                "title": "Team Dashboard",
                "path": "/dashboard/team",
                "icon": "users-round",
                "sort_order": 30,
                "permissions": [
                    "dashboard:read",
                    "dashboard:team",
                ],
            },
            {
                "code": "department_dashboard",
                "title": "Department Dashboard",
                "path": "/dashboard/department",
                "icon": "building",
                "sort_order": 40,
                "permissions": [
                    "dashboard:read",
                    "dashboard:department",
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
                    "project_members:manage",
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
            {
                "code": "resource_utilization",
                "title": "Resource Utilization",
                "path": "/resource-utilization",
                "icon": "activity",
                "sort_order": 50,
                "permissions": [
                    "resource_utilization:read",
                    "resource_utilization:employee",
                    "resource_utilization:team",
                    "resource_utilization:department",
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

CATALOG_PERMISSION_CODES = {
    perm_code
    for menu in MENUS
    for submenu in menu["submenus"]
    for perm_code in submenu["permissions"]
}

FULL_ACCESS_ROLES = {"SuperAdmin", "Admin"}

ROLE_PERMISSION_MAP = {
    "HOD": {
        "users:create",
        "users:read",
        "users:update",
        "departments:read",
        "departments:update",
        "projects:read",
        "projects:update",
        "tasks:read",
        "subtasks:read",
        "timesheets:read",
        "timesheets:approve",
        "timesheets:reject",
        "dashboard:department",
        "resource_utilization:department",
    },
    "Project Manager": {
        "users:read",
        "departments:read",
        "projects:create",
        "projects:read",
        "projects:update",
        "projects:delete",
        "project_members:manage",
        "tasks:create",
        "tasks:read",
        "tasks:update",
        "tasks:delete",
        "tasks:assign",
        "subtasks:create",
        "subtasks:read",
        "subtasks:update",
        "subtasks:delete",
        "timesheets:create",
        "timesheets:read",
        "timesheets:update",
        "timesheets:delete",
        "timesheets:approve",
        "timesheets:reject",
        "dashboard:project",
        "dashboard:team",
        "resource_utilization:team",
    },
    "Team Lead": {
        "users:read",
        "departments:read",
        "projects:read",
        "tasks:create",
        "tasks:read",
        "tasks:update",
        "tasks:assign",
        "subtasks:create",
        "subtasks:read",
        "subtasks:update",
        "subtasks:delete",
        "timesheets:create",
        "timesheets:read",
        "timesheets:update",
        "timesheets:delete",
        "timesheets:approve",
        "timesheets:reject",
        "dashboard:team",
        "resource_utilization:team",
    },
    "Developer": {
        "departments:read",
        "projects:read",
        "tasks:read",
        "subtasks:read",
        "subtasks:update",
        "timesheets:create",
        "timesheets:read",
        "timesheets:update",
        "timesheets:delete",
        "dashboard:employee",
        "resource_utilization:employee",
    },
    "Tester": {
        "departments:read",
        "projects:read",
        "tasks:read",
        "subtasks:read",
        "subtasks:update",
        "timesheets:create",
        "timesheets:read",
        "timesheets:update",
        "timesheets:delete",
        "dashboard:employee",
        "resource_utilization:employee",
    },
    "Business Analyst": {
        "departments:read",
        "projects:read",
        "tasks:read",
        "subtasks:read",
        "subtasks:update",
        "timesheets:create",
        "timesheets:read",
        "timesheets:update",
        "timesheets:delete",
        "dashboard:project",
        "resource_utilization:employee",
    },
}


def desired_permission_codes_for_role(role_name: str) -> set[str]:
    if role_name in FULL_ACCESS_ROLES:
        return set(CATALOG_PERMISSION_CODES)
    if role_name == "CEO":
        return {
            code
            for code in CATALOG_PERMISSION_CODES
            if code.endswith(":read")
        }
    return set(ROLE_PERMISSION_MAP.get(role_name, set()))

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

    perms_by_code = {perm.code: perm for perm in all_perms}

    for role_name, role_obj in roles_map.items():
        desired_codes = desired_permission_codes_for_role(role_name)
        custom_permissions = [
            perm
            for perm in role_obj.permissions
            if perm.code not in CATALOG_PERMISSION_CODES
        ]
        catalog_permissions = [
            perms_by_code[perm_code]
            for perm_code in sorted(desired_codes)
            if perm_code in perms_by_code
        ]
        role_obj.permissions = custom_permissions + catalog_permissions
                
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
