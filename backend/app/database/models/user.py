import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime,String,func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import mapped_column,Mapped,relationship
from ..base_class import Base

from .resume import Resume
from .interview import Interview
from .refresh_token import RefreshToken

class User(Base):
    __tablename__="users"

    id:Mapped[uuid.UUID]=mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email:Mapped[str]=mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash:Mapped[str | None]=mapped_column(
        String(255),
        nullable=True,
    )

    name:Mapped[str]=mapped_column(
        String(100),
        nullable=False,
    )
    
    google_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deleted_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    resumes: Mapped[list["Resume"]] = relationship(
        Resume,
        back_populates="user",
    )

    interviews: Mapped[list["Interview"]] = relationship(
        Interview,
        back_populates="user",
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        RefreshToken,
        back_populates="user",
        cascade="all, delete-orphan",
    )