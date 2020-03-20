from order.models import Order
from celery import shared_task

from order.utils import publish_created_order, sync_order_product_data, sync_order_user_data


@shared_task
def fetch_publish_order_data(order_id: int):
    """
    get product related data from product service
    get user related data from user related service
    publish order created message
    :param order_id: integer
    """
    order = Order.objects.get(pk=order_id)
    sync_order_product_data(order)
    sync_order_user_data(order)
    publish_created_order(order)
