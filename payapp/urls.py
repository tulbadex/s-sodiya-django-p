from django.urls import path
from . import views

app_name = 'payapp'
urlpatterns = [
    path('', views.index, name="home"),
    path('about', views.about, name="about"),
    path('how', views.how, name="how"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('transactions', views.transactions, name='transactions'),
    path('make_payment', views.make_payment, name='make_payment'),
    path('request_payments', views.request_payment, name='request_payments'),
    path('notification', views.notification, name='notification'), 
    path('handle_payment_request/<int:request_id>/<str:action>/', views.handle_payment_request, name='handle_payment_request'),
    path('conversion/<str:currency1>/<str:currency2>/<amount>', views.convert_currency, name='convert_currency'),
]