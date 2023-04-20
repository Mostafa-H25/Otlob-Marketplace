import uuid
from django.conf import settings
from django.shortcuts import reverse
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model


from user.models import Address


class Category(models.Model):
    name = models.CharField(unique=True, max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:category', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "Categories"


class Subcategory(models.Model):
    category = models.ForeignKey(
        Category, related_name='subcategory', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Subcategory, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:sub-category', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "Sub-categories"


class Brand(models.Model):
    category = models.ManyToManyField(Category)
    sub_category = models.ManyToManyField(Subcategory)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Brand, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('#', kwargs={'slug': self.slug})


def item_dir_path(instance, filename):
    return f'items/{instance.category.name}/{instance.sub_category.name}/{filename}'


class Item(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(
        Subcategory, on_delete=models.SET_NULL, blank=True, null=True)
    brand = models.ForeignKey(
        Brand, to_field='name', on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, default=uuid.uuid1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to=item_dir_path,
                             default='items/default.png')
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.name}-{self.brand}-{self.seller}")
        return super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:product', kwargs={'slug': self.slug})


class OrderItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        if self.item.discount_price:
            return self.quantity * self.item.discount_price
        else:
            return self.quantity * self.item.price

# def get_sentinel_user():
#     return get_user_model().objects.get_or_create(username='deleted')[0]


class Coupon(models.Model):
    user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True)
    # on_delete = models.SET(get_sentinel_user)
    code = models.UUIDField(default=uuid.uuid4, primary_key=True)
    discount = models.DecimalField(max_digits=3, decimal_places=2, )
    created_at = models.DateField(auto_now_add=True)
    expire_by = models.DateField()
    expired = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.code)

    # @property
    # def days_left(self):
    #     return (self.expired_at - self.created_at)

    class Meta:
        ordering = ('-created_at',)


class Order(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    created_date = models.DateField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        Address, related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        Address, related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    shipped = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Order - {self.uuid}"

    def get_order_url(self):
        return reverse("core:order-summary", kwargs={'pk': self.uuid})

    def get_checkout_url(self):
        return reverse("core:checkout", kwargs={'pk': self.uuid})

    def get_total(self):
        total = 0
        for item in self.items.all():
            total += item.get_total_item_price()
        return total

    def get_discount_total(self):
        discount_total = round(
            self.get_total() * (1 - self.coupon.discount), 2)
        return discount_total


class Stripe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id = models.CharField(max_length=255, primary_key=True)
