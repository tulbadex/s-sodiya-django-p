from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy
from . import views

# app_name = 'accounts'
urlpatterns = [
    path('signup/', views.signup_view, name="signup"),
    path('login/', views.login_view, name="login"),
    path('', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='accounts/registration/password_reset_form.html', success_url=reverse_lazy('password_reset_done')), name='reset_password'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/registration/password_reset_confirm.html', success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/registration/password_reset_complete.html'), name='password_reset_complete'),
]