from sqlalchemy import Column, String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ProductType(Base):
    __tablename__ = "product_types"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sysname = Column(String, nullable=False, unique=True, index=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Связи
    categories = relationship("Category", back_populates="product_type")
