from sqlalchemy.orm import Session
from sqlalchemy import func
from models.order.order_db import OrderTable
from models.user.user_db import User
from models.product.product_db import Product
from models.order.order_product_db import OrderProduct
from models.product.attachment_product_db import get_attachments_by_product_id
from models.driver.driver_db import DeliveryMan, DeliveryOrder

def get_order_info_by_order_id(db: Session, order_id: int):
    order = db.query(OrderTable).filter(OrderTable.order_id == order_id).first()
    if not order:
        return None

    user = db.query(User).filter(User.user_id == order.user_id).first()
    num_orders_by_user = db.query(func.count(OrderTable.order_id)).filter(OrderTable.user_id == order.user_id).scalar()

    driver = (
        db.query(DeliveryMan, DeliveryOrder)
        .join(DeliveryOrder, DeliveryOrder.delivery_id == DeliveryMan.delivery_id)
        .filter(DeliveryOrder.order_id == order_id)
        .first()
    )

    driver_data = driver[0] if driver else None

    order_products = (
        db.query(OrderProduct, Product)
        .join(Product, Product.product_id == OrderProduct.product_id)
        .filter(OrderProduct.order_id == order_id)
        .all()
    )

    product_details = []
    for op, prod in order_products:
        attachments = get_attachments_by_product_id(db, prod.product_id)
        product_details.append({
            "product_id": prod.product_id,
            "product_name": prod.product_name,
            "attachments": attachments,
            "price": prod.selling_price,
            "discount": prod.offer_percentage,
            "quantity": op.quantity
        })


    return {
        "order_id": order.order_id,
        "order_date": order.order_date,
        "estimated_delivery": order.estimated_delivery,
        "going_location": order.going_location,
        "receiver_name": order.receiver_name,
        "tracking_number": order.tracking_number,
        "user_email": user.user_email if user else "",
        "user_id": user.user_id if user else None,
        "number_of_orders_by_user": num_orders_by_user,
        "shipping_method": order.payment_method,
        "total_cost": order.total_price,
        "payment": order.payment,
        "products": product_details,
        "driver_name": driver_data.delivery_name if driver_data else None,
        "vehicle_id": driver_data.vehicle_id if driver_data else None,
        "driver_phone": driver_data.delivery_phone if driver_data else None,
        "driver_avatar": driver_data.delivery_photo if driver_data else None
    }
