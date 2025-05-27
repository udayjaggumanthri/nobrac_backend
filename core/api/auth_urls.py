from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    UserLoginView,
    UserProfileView,
    UserRegistrationView,
    CompanyProfileView
)

urlpatterns = [
    # Custom auth endpoints that match frontend expectations
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('company/profile/', CompanyProfileView.as_view(), name='company_profile'),
]
