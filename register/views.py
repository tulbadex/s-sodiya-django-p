from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from .forms import UserRegisterForm
from .models import UserProfile
from decimal import Decimal

def signup_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])

            currency = form.cleaned_data['currency']
            if currency == 'GBP':
                initial_balance = Decimal(1000)
            elif currency == 'USD':
                initial_balance = Decimal(1000) * Decimal(1.35)  # Assuming 1 GBP = 1.35 USD
            elif currency == 'EUR':
                initial_balance = Decimal(1000) * Decimal(1.18)  # Assuming 1 GBP = 1.18 EUR
            else:
                # Default to GBP if the selected currency is not recognized
                currency = 'GBP'
                initial_balance = Decimal(1000)

            user.save()  # Save the user instance first
            UserProfile.objects.create(user=user, currency=currency, account_balance=initial_balance)
            
            # Log in the user
            login(request, user)
            return redirect('payapp:home')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('payapp:home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('payapp:home')