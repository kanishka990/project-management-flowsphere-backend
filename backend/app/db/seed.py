import asyncio
import uuid
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db.session import AsyncSessionLocal as async_session
from app.db.init_db import init_db
from app.models.user_model import User
from app.models.role_model import Role
from app.models.department_model import Department
from app.core.security import hash_password

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

        default_pwd = hash_password("Password@123!")
        
        # Cache created users to easily assign reporting_manager_id
        user_id_cache = {}

        for u_data in test_users:
            stmt = select(User).where(User.emp_id == u_data["emp_id"])
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

if __name__ == "__main__":
    asyncio.run(run_seed())