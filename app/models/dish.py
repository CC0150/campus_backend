from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models import Base


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String, nullable=False)
    category = Column(String, nullable=False)
    sales = Column(Integer, default=0)
    shop_id = Column(String, ForeignKey("shops.id"))

    shop = relationship("Shop", back_populates="dishes")
