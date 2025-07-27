from sqlalchemy import Column, BigInteger, String, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from ..utils.db_connection import Base

class UserReference(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(BigInteger, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), nullable=False)
    phone = Column(String(20))
    role = Column(String(50))
    isactive = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP)

    # We don't need all the fields, just enough to validate user existence
    # No need for relationships here since we're just using this for validation 