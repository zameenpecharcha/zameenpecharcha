from sqlalchemy import Column, DateTime, String, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ..utils.db_connection import Base
import uuid
import enum

class TargetType(enum.Enum):
    POST = "post"
    COMMENT = "comment"
    PROPERTY = "property"

class Like(Base):
    __tablename__ = 'likes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    target_type = Column(SQLEnum(TargetType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True)) 