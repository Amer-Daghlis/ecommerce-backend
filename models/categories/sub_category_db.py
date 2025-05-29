from sqlalchemy import Column, Integer, String
from models.database import Base

class SubCategory(Base):
    __tablename__ = "sub_category"

    sub_category_id = Column(Integer, primary_key=True, index=True)
    sub_category_name = Column(String(255), nullable=False)
