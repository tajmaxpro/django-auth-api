"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated



schema_view = get_schema_view(
    openapi.Info(
        title="CustomUser - Token Authentication and Authorization API",
        default_version='v1',
        description="Welcome to the Authentication API! This API provides a step-by-step guide for user authentication and profile management. Follow these steps for effective API usage:\n"
                    "1. **Registration**: Start by creating a new user account.\n"
                    "2. **Login**: Log in with your registered account using your email and password. After providing your email and password, verify the OTP you receive to obtain the authentication token.\n"
                    "3. **Profile Management**: Retrieve your user profile and update your profile information (using the authentication token).\n"
                    "4. **Account Deletion**: If needed, delete your user account (using the authentication token).\n",
        contact=openapi.Contact(email="inbkhayrulloh@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[]
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('auths.urls')),

    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]