from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    BigInteger,
    Numeric,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, index=True)
    sku = Column(String, nullable=False, unique=True, index=True)  # Stock Keeping Unit
    price = Column(Numeric(10, 2), nullable=False)  # Цена с двумя знаками после запятой
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(
        BigInteger, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    amount = Column(Integer, default=0)  # Количество на складе
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    category = relationship("Category", back_populates="products")
    photos = relationship(
        "ProductPhoto", back_populates="product", cascade="all, delete-orphan"
    )
    carpet = relationship("Carpet", back_populates="product", uselist=False)
