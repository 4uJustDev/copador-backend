from sqlalchemy import Column, Integer, String, Text, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class ProductPhoto(Base):
    __tablename__ = "product_photos"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    filename = Column(String, nullable=False)
    filepath = Column(Text, nullable=False)
    thumbpath = Column(Text, nullable=False)
    is_main = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    # Связь с товаром
    product = relationship("Product", back_populates="photos")
