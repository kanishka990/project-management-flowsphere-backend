from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.password_reset_token_model import PasswordResetToken

class PasswordResetTokenRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used == False
        )
        return await self.session.scalar(stmt)

    async def create(self, token: PasswordResetToken) -> PasswordResetToken:
        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token

    async def update(self, token: PasswordResetToken, **kwargs) -> PasswordResetToken:
        for key, value in kwargs.items():
            if hasattr(token, key) and value is not None:
                setattr(token, key, value)
        await self.session.flush()
        await self.session.refresh(token)
        return token
