from sqlalchemy import Column, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    parent_id = Column(
        BigInteger, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )
    sysname = Column(String, nullable=False, unique=True, index=True)
    is_leaf = Column(Boolean, default=False)

    # Связи
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship(
        "Category", back_populates="parent", cascade="all, delete-orphan"
    )
    products = relationship("Product", back_populates="category")
