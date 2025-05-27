"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from farmers.views import FarmerViewSet
from companies.views import CompanyViewSet
from farmer_mappings.views import FarmerMappingViewSet
from volunteers.views import VolunteerViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'farmers', FarmerViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'farmer-mappings', FarmerMappingViewSet)
router.register(r'volunteers', VolunteerViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    # Add auth URLs
    path('api/auth/', include('api.auth_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
