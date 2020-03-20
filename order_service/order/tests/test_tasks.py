from unittest.mock import patch

from django.test import TestCase

from order.models import Order
from order.tasks import fetch_publish_order_data


@patch('order.tasks.sync_order_product_data', autospec=True)
@patch('order.tasks.sync_order_user_data', autospec=True)
@patch('order.tasks.publish_created_order', autospec=True)
class TestFetchPublishOrderDataTask(TestCase):
    def test_with_wrong_order_id(self, mock1, mock2, mock3):
        with self.assertRaises(Order.DoesNotExist):
            fetch_publish_order_data(5)
        self.assertFalse(mock1.called)
        self.assertFalse(mock2.called)
        self.assertFalse(mock3.called)

    def test_with_valid_order_id(self, mock1, mock2, mock3):
        order = Order.objects.create(product_code='1', user_id='1')
        fetch_publish_order_data(order.id)
        self.assertTrue(mock1.called)
        self.assertTrue(mock2.called)
        self.assertTrue(mock3.called)
