from django.urls import path
from .views import (register_user,
                    login_user,
                    verify_otp,
                    profile_user,
                    update_profile,
                    delete_user
                    )



urlpatterns = [
    path('register/', register_user, name='register-user'),
    path('login/', login_user, name='login-user'),
    path('verify/', verify_otp, name='verify-otp'),
    path('profile/', profile_user, name='profile-user'),
    path('update/', update_profile, name='update-profile'),
    path('delete/', delete_user, name='delete-user')
]