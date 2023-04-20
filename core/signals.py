from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Item, Brand, Order, OrderItem


@receiver(pre_save, sender=Item)
def create_brand(sender, instance, **kwargs):
    if instance.brand:
        if not Brand.objects.filter(name=instance.brand).exists():
            Brand.objects.create(name=instance.brand)
            Brand.category.set(instance.category)
            Brand.sub_category.set(instance.sub_category)

# @receiver(pre_save, sender=OrderItem)
# def create_order(sender, instance, **kwargs):
#     if instance.brand:
#         if not Brand.objects.filter(name=instance.brand).exists():
#             Brand.objects.create(name=instance.brand)
#             Brand.category.set(instance.category)
#             Brand.sub_category.set(instance.sub_category)
