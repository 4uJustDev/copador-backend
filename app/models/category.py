from sqlalchemy import Column, String, ForeignKey, BigInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    parent_id = Column(BigInteger, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    sysname = Column(String, nullable=False, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category")
