from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from order.models import Order


class TestOrderAPIView(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('order_api')

    def test_get(self):
        response = self.client.get(self.url, data={})
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_patch(self):
        response = self.client.patch(self.url, data={})
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_put(self):
        response = self.client.put(self.url, data={})
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_delete(self):
        response = self.client.delete(self.url, data={})
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_post_empty(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(
            {"user_id": ["This field is required."], "product_code": ["This field is required."]},
            response.json()
        )

    @patch('order.views.fetch_publish_order_data.delay', autospec=True)
    def test_post_valid(self, task_mock):
        data = {"user_id": "123", "product_code": "334"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(
            {"user_id": "123", "product_code": "334"},
            response.json()
        )
        order = Order.objects.get(**data)
        self.assertTrue(task_mock.called)
        task_mock.assert_called_with(order.id)
