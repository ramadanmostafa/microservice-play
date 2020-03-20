from rest_framework.generics import CreateAPIView

from order.serializers import OrderSerializer

from .tasks import fetch_publish_order_data


class OrderAPIView(CreateAPIView):
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save()
        fetch_publish_order_data.delay(serializer.instance.id)
