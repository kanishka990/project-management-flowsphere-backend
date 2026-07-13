from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base_repository import BaseRepository
from app.models.email_verification_token_model import EmailVerificationToken
from uuid import UUID

class EmailVerificationTokenRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_token_hash(self, token_hash: str) -> EmailVerificationToken | None:
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash,
            EmailVerificationToken.used == False
        )
        return await self.session.scalar(stmt)

    async def create(self, token: EmailVerificationToken) -> EmailVerificationToken:
        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token

    async def update(self, token: EmailVerificationToken, **kwargs) -> EmailVerificationToken:
        for key, value in kwargs.items():
            if hasattr(token, key) and value is not None:
                setattr(token, key, value)
        await self.session.flush()
        await self.session.refresh(token)
        return token
