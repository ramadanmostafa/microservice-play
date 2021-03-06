# Generated by Django 3.0.4 on 2020-03-08 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=512)),
                ('product_code', models.CharField(max_length=512)),
                ('customer_fullname', models.CharField(blank=True, max_length=512)),
                ('product_name', models.CharField(blank=True, max_length=512)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=14, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
            ],
        ),
    ]
