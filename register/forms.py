from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
  CURRENCY_CHOICES = [
        ('GBP', 'GB Pounds'),
        ('USD', 'US Dollars'),
        ('EUR', 'Euros'),
    ]
  username = forms.CharField(max_length=20)
  first_name = forms.CharField(max_length=30)
  last_name = forms.CharField(max_length=30)
  email = forms.EmailField(max_length=254)
  currency = forms.ChoiceField(choices=CURRENCY_CHOICES)

  class Meta:
      model = User
      fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'currency',]