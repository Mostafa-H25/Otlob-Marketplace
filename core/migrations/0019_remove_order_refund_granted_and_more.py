# Generated by Django 4.2 on 2023-04-19 19:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_coupon_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='refund_granted',
        ),
        migrations.RemoveField(
            model_name='order',
            name='refund_requested',
        ),
    ]
