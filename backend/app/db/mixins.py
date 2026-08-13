from uuid import UUID
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class FullAuditMixin:
    """
    A comprehensive mixin for tracking timestamps, user actions, 
    and safe soft-deletions in the database.
    """
    
    # 1. Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False
    )

    # 2. User Tracking (Assuming user IDs are integers or strings)
    # These are Optional because some actions might be done by the system itself
    created_by: Mapped[Optional[UUID]] = mapped_column(index=True)
    updated_by: Mapped[Optional[UUID]] = mapped_column(index=True)

    # 3. Soft Deletes
    is_deleted: Mapped[bool] = mapped_column(
        default=False, 
        index=True
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        default=None
    )
    
    deleted_by: Mapped[Optional[UUID]] = mapped_column(default=None)