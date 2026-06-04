from sqlalchemy import Column, String, Float, Integer, JSON
from sqlalchemy.orm import relationship

from app.models import Base


class Shop(Base):
    __tablename__ = "shops"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    rating = Column(Float, default=5.0)
    sales = Column(Integer, default=0)
    min_order = Column(Float, default=0)
    delivery_fee = Column(Float, default=0)
    delivery_time = Column(Integer, default=30)
    notice = Column(String, default="")
    tags = Column(JSON, default=list)
    discount = Column(String, default="")
    bulletin = Column(String, default="")
    image = Column(String, default="🍽️")

    dishes = relationship("Dish", back_populates="shop")
