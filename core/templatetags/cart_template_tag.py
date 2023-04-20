from django import template
from ..models import Order
from user.models import Conversation

register = template.Library()


@register.filter
def cart_items_count(user):
    if user.is_authenticated:
        queryset = Order.objects.filter(user=user, ordered=False).first()
        if queryset:
            return queryset.items.count()
    return 0


@register.filter
def inbox_conversations_count(user):
    if user.is_authenticated:
        queryset = Conversation.objects.filter(
            members=user)
        print(queryset)
        if queryset:
            return queryset.count()
    return 0
