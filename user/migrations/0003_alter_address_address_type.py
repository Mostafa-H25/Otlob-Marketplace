# Generated by Django 4.1.7 on 2023-03-25 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_profile_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address_type',
            field=models.CharField(choices=[('B', 'Billing Address'), ('S', 'Shipping Address')], default='B', max_length=1),
        ),
    ]
