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
        "code": "setup", "name": "Setup & Configuration",
        "submenus": [
            {
                "code": "user_mgt", "title": "User Management",
                "permissions": ["users:create", "users:read", "users:update", "users:delete"]
            },
            {
                "code": "role_mgt", "title": "Role Management",
                "permissions": ["roles:create", "roles:read", "roles:update", "roles:delete"]
            },
            {
                "code": "perm_mgt", "title": "Permission Management",
                "permissions": ["permissions:create", "permissions:read", "permissions:update", "permissions:delete"]
            },
            {
                "code": "menu_mgt", "title": "Menu Management",
                "permissions": ["menus:create", "menus:read", "menus:update", "menus:delete", "submenus:create", "submenus:read", "submenus:delete"]
            }
        ]
    }
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
        stmt = insert(Menu).values(id=uuid.uuid4(), code=m_data["code"], name=m_data["name"])
        stmt = stmt.on_conflict_do_update(
            index_elements=['code'], set_=dict(name=stmt.excluded.name)
        ).returning(Menu.id)
        menu_id = await session.scalar(stmt)

        for sub_data in m_data["submenus"]:
            sub_stmt = insert(SubMenu).values(
                id=uuid.uuid4(), code=sub_data["code"], title=sub_data["title"], menu_id=menu_id
            )
            sub_stmt = sub_stmt.on_conflict_do_update(
                index_elements=['code'], set_=dict(title=sub_stmt.excluded.title, menu_id=sub_stmt.excluded.menu_id)
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