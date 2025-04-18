from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session
from models.database import Base

class AttachmentProduct(Base):
    __tablename__ = "attachmentproduct"

    attachment_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.product_id"))
    attachment_link = Column(String(255))

def get_attachments_by_product_id(db: Session, product_id: int):
    results = db.query(AttachmentProduct).filter(AttachmentProduct.product_id == product_id).all()
    return [a.attachment_link for a in results]
