import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

from app.models.user_model import User
from app.models.role_model import Role
from app.models.permission_model import Permission
from app.models.menu_model import Menu
from app.models.submenu_model import SubMenu
from app.core.security import hash_password

# --- CATALOG DEFINITION ---
MENUS = [
    {
        "code": "sys_config", "name": "System Configuration",
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
    {"name": "SuperAdmin", "description": "System owner with absolute access"},
    {"name": "Admin", "description": "Administrator with system management access"},
    {"name": "Project Manager", "description": "Manages projects and teams"},
    {"name": "Viewer", "description": "Read-only access"}
]

async def init_db(session: AsyncSession):
    print("Starting Database Initialization...")

    # 1. UPSERT MENUS & SUBMENUS & PERMISSIONS
    for m_data in MENUS:
        # Upsert Menu
        stmt = insert(Menu).values(id=uuid.uuid4(), code=m_data["code"], name=m_data["name"])
        stmt = stmt.on_conflict_do_update(
            index_elements=['code'], 
            set_=dict(name=stmt.excluded.name)
        ).returning(Menu.id)
        menu_id = await session.scalar(stmt)

        for sub_data in m_data["submenus"]:
            # Upsert SubMenu
            sub_stmt = insert(SubMenu).values(
                id=uuid.uuid4(), code=sub_data["code"], title=sub_data["title"], menu_id=menu_id
            )
            sub_stmt = sub_stmt.on_conflict_do_update(
                index_elements=['code'],
                set_=dict(title=sub_stmt.excluded.title, menu_id=sub_stmt.excluded.menu_id)
            ).returning(SubMenu.id)
            submenu_id = await session.scalar(sub_stmt)

            # Upsert Permissions
            for perm_code in sub_data["permissions"]:
                action = perm_code.split(":")[-1]
                p_stmt = insert(Permission).values(
                    id=uuid.uuid4(), code=perm_code, action=action, 
                    description=f"Can {action} {perm_code.split(':')[0]}", submenu_id=submenu_id
                )
                p_stmt = p_stmt.on_conflict_do_update(
                    index_elements=['code'],
                    set_=dict(submenu_id=p_stmt.excluded.submenu_id, description=p_stmt.excluded.description)
                )
                await session.execute(p_stmt)

    # 2. UPSERT ROLES
    for r_data in DEFAULT_ROLES:
        r_stmt = insert(Role).values(
            id=uuid.uuid4(), name=r_data["name"], description=r_data["description"]
        )
        r_stmt = r_stmt.on_conflict_do_update(
            index_elements=['name'],
            set_=dict(description=r_stmt.excluded.description)
        )
        await session.execute(r_stmt)
    
    await session.commit()

    # 3. ASSIGN PERMISSIONS TO ROLES (E.g., 'Admin' gets everything except role/perm deletion)
    admin_role = (await session.scalars(select(Role).where(Role.name == "Admin"))).first()
    all_perms = (await session.scalars(select(Permission))).all()
    
    if admin_role:
        # Prevent appending duplicates logic
        current_perm_ids = {p.id for p in admin_role.permissions}
        for perm in all_perms:
            if perm.id not in current_perm_ids and not perm.code.endswith(":delete"):
                admin_role.permissions.append(perm)
        await session.commit()

    # 4. UPSERT DEFAULT SUPERADMIN USER
    admin_emp_id = "EMP000001"
    stmt = select(User).where(User.emp_id == admin_emp_id)
    admin_user = (await session.execute(stmt)).scalar_one_or_none()

    if not admin_user:
        super_admin_role = (await session.scalars(select(Role).where(Role.name == "SuperAdmin"))).first()
        admin_user = User(
            id=uuid.uuid4(),
            emp_id=admin_emp_id,
            email="admin@yourcompany.com",
            first_name="System",
            last_name="Admin",
            phone_number="0000000000",
            hashed_password=hash_password("Password@123!"),
            is_active=True,
            is_verified=True,
            is_first_login=False
        )
        admin_user.roles.append(super_admin_role)
        session.add(admin_user)
        await session.commit()
    
    print("Database Initialization Complete.")