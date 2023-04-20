from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils.text import slugify


from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

import uuid
from datetime import timedelta
from PIL import Image


ADDRESS_CHOICES = (
    ('B', 'Billing Address'),
    ('S', 'Shipping Address'),
)


def user_dir_path(instance, filename):
    return f"profile-pics/user_{instance.user.id}/{filename}"


class Profile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField()
    phone_number = PhoneNumberField(unique=True)
    birthday = models.DateField()
    image = models.ImageField(
        upload_to=user_dir_path, default='profile-pics/default.png')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('auth:profile', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(
            f"{self.user.username}-{self.user.first_name}-{self.user.last_name}")
        return super(Profile, self).save(*args, **kwargs)

    # def save(self):
    #     super().save()

    #     img = Image.open(self.image.path)

    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    apartment = models.CharField(max_length=100)
    building = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = CountryField(blank_label="(select country)")
    zip = models.CharField(max_length=50)
    address_type = models.CharField(
        choices=ADDRESS_CHOICES, default='B', max_length=1)
    default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Conversation(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL)

    def __str__(self) -> str:
        return str(self.uuid)

    def get_absolute_url(self):
        return reverse('user:conversation', kwargs={'pk': self.uuid})

    class Meta:
        ordering = ('-modified_at',)


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f'{self.conversation.uuid} - {self.created_at}'

    class Meta:
        ordering = ('created_at',)
