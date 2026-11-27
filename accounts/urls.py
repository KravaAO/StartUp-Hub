
from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.urls')),
]

from .views import (
    CustomLoginView,
    register_view,
    profile_view,
    logout_view
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
]
