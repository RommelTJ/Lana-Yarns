# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-28 00:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0004_auto_20160625_0008'),
        ('orders', '0003_auto_20160627_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipping_total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=50)),
                ('order_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=50)),
                ('billing_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_address', to='orders.UserAddress')),
                ('cart', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='carts.Cart')),
                ('shipping_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_address', to='orders.UserAddress')),
                ('user_checkout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.UserCheckout')),
            ],
        ),
    ]
