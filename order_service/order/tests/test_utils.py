import json
from datetime import datetime
from functools import partial
from unittest.mock import patch, Mock

from django.conf import settings
from django.test import TestCase

from order.models import Order
from order.utils import publish_created_order, sync_order_product_data, sync_order_user_data, _add_get_request


def mock_date(year, month, day):
    return datetime(year, month, day)


class TestUtils(TestCase):
    def setUp(self) -> None:
        self.order = Order.objects.create(product_code='1', user_id='1')

    @patch('order.utils.timezone.now', new=partial(mock_date, year=2020, day=1, month=1))
    @patch('order.utils.pika.BlockingConnection.channel', autospec=True)
    def test_publish_created_order_with_minimum_data(self, mock):
        m = Mock()
        mock.return_value = m
        publish_created_order(self.order)
        self.assertTrue(m.basic_publish.called)
        m.basic_publish.assert_called_with(
            exchange='orders', routing_key='created_order', body=json.dumps({
                "producer": "order_service", "sent_at": mock_date(year=2020, month=1, day=1).isoformat(),
                "type": "created_order",
                "payload": {
                    "order": {
                        "order_id": str(self.order.id), "customer_fullname": "", "product_name": "",
                        "total_amount": None, "created_at": self.order.created_at.isoformat()
                    }
                }
            })
        )

    @patch('order.utils.timezone.now', new=partial(mock_date, year=2020, day=1, month=1))
    @patch('order.utils.pika.BlockingConnection.channel', autospec=True)
    def test_publish_created_order_with_full_data(self, mock):
        self.order.customer_fullname = 'Ramadan Khlaifa'
        self.order.product_name = "Iron man Suit"
        self.order.total_amount = 500.55
        m = Mock()
        mock.return_value = m
        publish_created_order(self.order)
        self.assertTrue(m.basic_publish.called)
        m.basic_publish.assert_called_with(
            exchange='orders', routing_key='created_order', body=json.dumps({
                "producer": "order_service", "sent_at": mock_date(year=2020, month=1, day=1).isoformat(),
                "type": "created_order",
                "payload": {
                    "order": {
                        "order_id": str(self.order.id), "customer_fullname": "Ramadan Khlaifa",
                        "product_name": "Iron man Suit", "total_amount": 500.55,
                        "created_at": self.order.created_at.isoformat()
                    }
                }
            })
        )

    @patch('order.utils._add_get_request', autospec=True, return_value={})
    def test_sync_order_product_data_empty(self, mock):
        sync_order_product_data(self.order)
        self.assertTrue(mock.called)
        mock.assert_called_with(url=settings.PRODUCTS_SERVICE_URL.format(product_code=self.order.product_code))
        self.order.refresh_from_db()
        self.assertIsNone(self.order.total_amount)
        self.assertEqual('', self.order.product_name)

    @patch('order.utils._add_get_request', autospec=True, return_value={'name': 'Iron man Suit', 'price': 555.55})
    def test_sync_order_product_data_full(self, mock):
        sync_order_product_data(self.order)
        self.assertTrue(mock.called)
        mock.assert_called_with(url=settings.PRODUCTS_SERVICE_URL.format(product_code=self.order.product_code))
        self.order.refresh_from_db()
        self.assertEqual('Iron man Suit', self.order.product_name)
        self.assertEqual(555.55, float(self.order.total_amount))

    @patch('order.utils._add_get_request', autospec=True, return_value={})
    def test_sync_order_user_data_data_empty(self, mock):
        sync_order_user_data(self.order)
        self.assertTrue(mock.called)
        mock.assert_called_with(url=settings.USERS_SERVICE_URL.format(user_id=self.order.user_id))
        self.order.refresh_from_db()
        self.assertEqual('', self.order.customer_fullname)

    @patch('order.utils._add_get_request', autospec=True, return_value={'firstName': 'Ramadan', 'lastName': 'Khalifa'})
    def test_sync_order_user_data_data_full(self, mock):
        sync_order_user_data(self.order)
        self.assertTrue(mock.called)
        mock.assert_called_with(url=settings.USERS_SERVICE_URL.format(user_id=self.order.user_id))
        self.order.refresh_from_db()
        self.assertEqual('Ramadan Khalifa', self.order.customer_fullname)

    @patch('order.utils.requests.get')
    def test__add_get_request_200(self, mock):
        m = Mock()
        m.status_code = 200
        m.json.return_value = {'data': ''}
        mock.return_value = m
        self.assertEqual({'data': ''}, _add_get_request('test'))

    @patch('order.utils.requests.get')
    def test__add_get_request_500(self, mock):
        m = Mock()
        m.status_code = 500
        m.json.return_value = {'data': ''}
        mock.return_value = m
        self.assertEqual({}, _add_get_request('test'))
