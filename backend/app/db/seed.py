import asyncio
from sqlalchemy import select
# Import your specific models and your init_db function
from app.db.session import AsyncSessionLocal as async_session
from app.models.user_model import User
from app.db.init_db import init_db 

async def run_seed():
    # Use the session factory to create a session
    async with async_session() as session:
        # Check if Admin already exists using the correct select syntax (optional logging, init_db handles actual check)
        stmt = select(User).where(User.emp_id == "EMP000001")
        result = await session.execute(stmt)
        
        if result.scalar_one_or_none():
            print("Admin user already exists. Seeding will update menus, submenus, permissions and roles.")
        
        # Call the logic that actually upserts and creates the user and role
        await init_db(session)
        print("Database seeded successfully.")

if __name__ == "__main__":
    asyncio.run(run_seed())