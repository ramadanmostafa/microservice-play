from django.db import models


class Order(models.Model):
    user_id = models.CharField(max_length=512)
    product_code = models.CharField(max_length=512)
    customer_fullname = models.CharField(max_length=512, blank=True)
    product_name = models.CharField(max_length=512, blank=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    created_at = models.DateTimeField('date created', auto_now_add=True)
