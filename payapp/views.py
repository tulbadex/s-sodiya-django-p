from django.contrib.auth.decorators import login_required
from .forms import PaymentForm, PaymentRequestForm
from register.models import UserProfile
from .models import Transaction, PaymentRequest
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction
from .utils import get_currency_symbol

def index(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def how(request):
    return render(request, 'how.html')

@login_required
def dashboard(request):
    user = UserProfile.objects.get(user=request.user)
    user_currency_symbol = get_currency_symbol(user)
    return render(request, 'auth/home.html', {'user': user, 'currency': user_currency_symbol})

@login_required
def make_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient_username']
            amount = form.cleaned_data['amount']

            try:
                recipient_profile = UserProfile.objects.get(user__username=recipient_username)
            except UserProfile.DoesNotExist:
                recipient_profile = UserProfile.objects.create(user=User.objects.get(username=recipient_username), account_balance=1000)

            sender_profile = UserProfile.objects.get(user=request.user)
            if sender_profile.account_balance < amount:
                messages.error(request, 'Insufficient balance.')
                return redirect('payapp:make_payment')
            
            sender_profile.account_balance -= amount
            sender_profile.save()

            recipient_profile.account_balance += amount
            recipient_profile.save()

            Transaction.objects.create(sender=request.user, recipient=recipient_profile.user, amount=amount)

            messages.success(request, 'Payment successfully sent.')
            return redirect('payapp:dashboard')
    else:
        form = PaymentForm()
        return render(request, 'auth/make_payment.html', {'form': form})
    
@login_required
def request_payment(request):
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient_username']
            amount_requested = form.cleaned_data['amount']
            PaymentRequest.objects.create(
                sender=request.user,
                recipient=User.objects.get(username=recipient_username),
                amount=amount_requested
            )
            messages.success(request, f'Payment request sent to {recipient_username}.')
            return redirect('payapp:dashboard')
    else:
        form = PaymentRequestForm()
    return render(request, 'auth/request_payments.html', {'form': form})
    
@login_required
def transactions(request):
    user = UserProfile.objects.get(user=request.user)
    user_currency_symbol = get_currency_symbol(user)
    transactions = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(recipient=request.user)
    return render(request, 'auth/transactions.html', {'transactions': transactions, 'currency': user_currency_symbol})

@login_required
def notification(request):
    pending_requests = PaymentRequest.objects.filter(recipient=request.user, status='pending')
    
    sender_profiles = [UserProfile.objects.get(user=request.sender) for request in pending_requests]
    user_currency_symbols = [get_currency_symbol(profile) for profile in sender_profiles]

    # Pair each pending request with its corresponding currency symbol using zip
    pending_requests_with_symbols = zip(pending_requests, user_currency_symbols)

    return render(request, 'auth/notification.html', {'pending_requests_with_symbols': pending_requests_with_symbols})

@login_required
def handle_payment_request(request, request_id, action):
    payment_request = get_object_or_404(PaymentRequest, id=request_id)
    
    # Ensure that only the recipient of the payment request can handle it
    if payment_request.recipient != request.user:
        messages.error(request, 'You are not authorized to handle this payment request.')
        return redirect('payapp:dashboard')
    
    if action == 'accept':
        with transaction.atomic():
            # Update status to accepted
            payment_request.status = 'accepted'
            payment_request.save()
            
            # Deduct amount from recipient's balance and add to sender's balance
            sender_profile = UserProfile.objects.get(user=payment_request.sender)
            recipient_profile = UserProfile.objects.get(user=payment_request.recipient)
            if recipient_profile.account_balance < payment_request.amount:
                messages.error(request, 'Insufficient balance to accept payment request.')
                return redirect('payapp:dashboard')
            
            recipient_profile.account_balance -= payment_request.amount
            sender_profile.account_balance += payment_request.amount
            
            recipient_profile.save()
            sender_profile.save()
            
            messages.success(request, f'Payment request sent by {payment_request.sender} accepted.')
            return redirect('payapp:dashboard')
    elif action == 'reject':
        # Update status to rejected
        payment_request.status = 'rejected'
        payment_request.save()
        messages.success(request, f'Payment request sent by {payment_request.sender} rejected.')
    else:
        messages.error(request, 'Invalid action.')
    
    return redirect('payapp:dashboard')

ALLOWED_CURRENCIES = ['USD', 'EUR', 'GBP']  # Example list of allowed currencies
CONVERSION_RATES = {
    ('USD', 'EUR'): 0.93,  # Conversion rate from USD to EUR
    ('EUR', 'USD'): 1.08,  # Conversion rate from EUR to USD
    ('USD', 'GBP'): 0.80,  # Conversion rate from USD to GBP
    ('GBP', 'USD'): 1.26,  # Conversion rate from GBP to USD
    # Add more conversion rates as needed
}

def convert_currency(request, currency1, currency2, amount):
    try:
        amount = float(amount)
    except ValueError:
        messages.error(request, 'Amount must be a valid floating point number.')
        return render(request, 'auth/converter.html')

    if currency1 not in ALLOWED_CURRENCIES or currency2 not in ALLOWED_CURRENCIES:
        messages.error(request, 'One or both of the provided currencies are not supported.')
        return render(request, 'auth/converter.html')

    if (currency1, currency2) not in CONVERSION_RATES:
        messages.error(request, 'Conversion rate not available for the provided currency pair.')
        return render(request, 'auth/converter.html')

    conversion_rate = CONVERSION_RATES[(currency1, currency2)]
    converted_amount = amount * conversion_rate

    response_data = {
        'currency1': currency1,
        'currency2': currency2,
        'amount': amount,
        'converted_to': converted_amount
    }
    return render(request, 'auth/converter.html', {'data': response_data})

