from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    UserProfileView,
    ChangePasswordView,
    UserDeleteView,
    RegisterView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('delete-account/', UserDeleteView.as_view(), name='delete-account'),
]


