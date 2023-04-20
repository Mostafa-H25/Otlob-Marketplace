from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django_countries.widgets import CountrySelectWidget

import json

from .models import Profile, Address, Message


with open('countries.json') as f:
    data = json.load(f)

countries = []
for country in data['countries']:
    ctr = (country['alpha-2'], country['name'])
    countries.append(ctr)


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Your Message'
            }),
        }


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Your Username'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your Email Address'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Your First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Your Last Name'
            })
        }


class ProfileForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Profile
        fields = ['birthday', 'phone_number', 'image']
        widgets = {
            'phone': PhoneNumberPrefixWidget(country_choices=countries),
            'birthday': forms.DateTimeInput(attrs={
                'placeholder': 'Select Birth Date',
                'type': 'date'
            }),
        }


class AddressForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Address
        fields = ['apartment', 'building', 'street',
                  'district', 'city', 'country', 'zip', 'default']
        widgets = {
            'apartment': forms.TextInput(attrs={
                'placeholder': 'Your Apartment No.'
            }),
            'building': forms.TextInput(attrs={
                'placeholder': 'Your Building No.'
            }),
            'street': forms.TextInput(attrs={
                'placeholder': 'Your Street Name'
            }),
            'district': forms.TextInput(attrs={
                'placeholder': 'Your District Name'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'Your City'
            }),
            'country': CountrySelectWidget(),
            'zip': forms.TextInput(attrs={
                'placeholder': 'Your Zipcode'
            }),
            'default': forms.CheckboxInput(),
        }


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)

    class Meta:
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Your Username'
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': 'Your Password'
            }),
        }


class RegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name',
                  'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Your Username'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your Email Address'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Your First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Your Last Name'
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Your Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Repeat Password'
            }),
        }
