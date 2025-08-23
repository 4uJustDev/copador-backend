from sqlalchemy import Column, Integer, String, Text, ForeignKey, BigInteger, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class Carpet(Base):
    __tablename__ = "carpets"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Специфичные характеристики ковра
    width = Column(Numeric(8, 2), nullable=True)  # Ширина в см
    length = Column(Numeric(8, 2), nullable=True)  # Длина в см
    material = Column(String, nullable=True)  # Материал (шерсть, шелк, хлопок и т.д.)
    origin = Column(
        String, nullable=True
    )  # Происхождение (персидский, турецкий и т.д.)
    age = Column(String, nullable=True)  # Возраст ковра
    condition = Column(
        String, nullable=True
    )  # Состояние (отличное, хорошее, удовлетворительное)

    # Связь с основным товаром
    product = relationship("Product", back_populates="carpet")

    def __repr__(self):
        return f"<Carpet(id={self.id}, product_id={self.product_id}, width={self.width}, length={self.length})>"
