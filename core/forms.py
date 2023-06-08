from django import forms

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .models import Item, OrderItem, Coupon, Category, Subcategory, Brand

import json


with open('countries.json') as f:
    data = json.load(f)

countries = []
for country in data['countries']:
    ctr = (country['alpha-2'], country['name'])
    countries.append(ctr)

PAYMENT_OPTIONS = (
    ('P', 'Paypal'),
    ('S', 'Stripe'),
    ('D', 'Debit'),
)


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'sub_category']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Brand Name',
            })
        }


# BrandFormset = forms.inlineformset_factory(
#     Subcategory, Brand, fields=('name',))


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['name', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Sub-Category Name',
            })
        }


SubcategoryFormset = forms.inlineformset_factory(
    Category, Subcategory, fields=('name',))


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name',]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Category Name',
            })
        }


CategoryFormset = forms.modelformset_factory(Category, fields=('name',))


class UserCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code',]
        widgets = {
            'expired': forms.TextInput(attrs={
                'placeholder': 'Your Promocode',
            })
        }


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['discount', 'expire_by']
        widgets = {
            'discount': forms.NumberInput(attrs={
                'placeholder': 'Discount Amount (0 ~ 1)',
                'min': 0,
                'max': 1,
            }),
            'expire_by': forms.DateInput(attrs={
                'placeholder': 'Expiry Date',
                'type': 'date'
            })
        }


class ShippingAddressForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    apartment = forms.CharField(max_length=100, required=False)
    building = forms.CharField(max_length=100, required=False)
    street = forms.CharField(max_length=255, required=False)
    district = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100, required=False)
    country = CountryField(
        blank_label="(select country)", blank=True).formfield()
    zip = forms.CharField(max_length=50, required=False)
    default = forms.BooleanField(
        initial=False, required=False, label='Shipping Address same as Billing Address')

    class Meta:
        widgets = {
            'apartment': forms.TextInput(attrs={
                'placeholder': 'Your Apartment No.',
                'required': False
            }),
            'building': forms.TextInput(attrs={
                'placeholder': 'Your Building No.',
                'required': False
            }),
            'street': forms.TextInput(attrs={
                'placeholder': 'Your Street Name',
                'required': False
            }),
            'district': forms.TextInput(attrs={
                'placeholder': 'Your District Name',
                'required': False
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'Your City',
                'required': False
            }),
            'country': CountrySelectWidget(),
            'zip': forms.TextInput(attrs={
                'placeholder': 'Your Zipcode',
                'required': False
            }),
            'default': forms.CheckboxInput(attrs={
                'required': False
            }),
        }


class PaymentMethodForm(forms.Form):
    payment_choice = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_OPTIONS)


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['quantity']


class ItemCreateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'image', 'category', 'sub_category', 'brand',
                  'price', 'quantity', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Product Name'
            }),
            'category': forms.Select(),
            'sub_category': forms.Select(),
            'brand': forms.TextInput(attrs={
                'placeholder': 'Brand Name'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': 'Product Price',
                'min': 1,
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'Product Quantity',
                'min': 1,
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Product Description',
                'rows': 6
            }),
        }
