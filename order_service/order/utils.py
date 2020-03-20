import pika
import json
import requests
import logging

from django.conf import settings
from django.utils import timezone
from rest_framework import status

from order.models import Order


logger = logging.getLogger(__name__)


def publish_created_order(order: Order) -> None:
    """
    publish order created message to rabbitmq
    """
    credentials = pika.PlainCredentials(settings.RABBIT_MQ_USERNAME, settings.RABBIT_MQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=settings.RABBIT_MQ_HOST, port=settings.RABBIT_MQ_PORT_NUMBER, credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='default')
    data = {
        "producer": "order_service",
        "sent_at": timezone.now().isoformat(),
        "type": "created_order",
        "payload": {
            "order": {
                "order_id": str(order.id),
                "customer_fullname": order.customer_fullname,
                "product_name": order.product_name,
                "total_amount": order.total_amount,
                "created_at": order.created_at.isoformat()
            }
        }
    }
    channel.basic_publish(
        exchange='orders', routing_key='created_order', body=json.dumps(data)
    )
    connection.close()


def sync_order_product_data(order: Order) -> None:
    """
    fetch product related data for a given order from the product service.
    """
    product_data = _add_get_request(url=settings.PRODUCTS_SERVICE_URL.format(product_code=order.product_code))
    order.product_name = product_data.get('name', '')
    order.total_amount = product_data.get('price')
    order.save()


def sync_order_user_data(order: Order) -> None:
    """
    fetch user related data for a given order from the user service.
    """
    user_data = _add_get_request(url=settings.USERS_SERVICE_URL.format(user_id=order.user_id))
    last_name = user_data.get('lastName', '')
    order.customer_fullname = user_data.get('firstName', '')
    if last_name:
        order.customer_fullname += ' ' + last_name
    order.save()


def _add_get_request(url: str) -> dict:
    """
    execute a get request to the given url and returns the response data if the response code is 200
    otherwise it logs the error and returns empty dict
    :param url: full URL of the service
    :return: response data in json format
    """
    response = requests.get(url=url, headers={'Content-Type': 'application/json'})

    if response.status_code != status.HTTP_200_OK:
        logger.error('Unable to fetch data URL:{}, response_code:{}\nresponse:{}'.format(
            url, response.status_code, response.text
        ))
        return dict()
    return response.json()
