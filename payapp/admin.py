from django.contrib import admin

# Register your models here.
from .models import PaymentRequest, Transaction

# Register your models here.
admin.site.register(PaymentRequest)
admin.site.register(Transaction)