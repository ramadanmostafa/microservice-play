from rest_framework.serializers import ModelSerializer

from order.models import Order


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ('user_id', 'product_code')
