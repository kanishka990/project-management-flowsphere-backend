# app/db/init_db.py
from app.models.user_model import User
from app.models.role_model import Role
from app.core.security import hash_password
import uuid

async def init_db(session):
    # 1. Create the 'SuperAdmin' Role
    admin_role = Role(name="SuperAdmin", description="System owner")
    session.add(admin_role)
    await session.flush() # Flush to get the role ID

    # 2. Create the first Admin User
    admin = User(
        id=uuid.uuid4(),
        emp_id="EMP000001",
        email="admin@yourcompany.com",
        first_name="System",
        last_name="Admin",
        phone_number="0000000000",
        hashed_password=hash_password("SuperSecretPassword123!"),
        is_active=True,
        is_verified=True,
        is_first_login=False
    )
    admin.roles.append(admin_role)
    session.add(admin)
    await session.commit()