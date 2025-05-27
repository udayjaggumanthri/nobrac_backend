from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from companies.views import CompanyViewSet
from volunteers.views import VolunteerViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'volunteers', VolunteerViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    # Include auth-specific URLs
    path('auth/', include('api.auth_urls')),

    # Include the router URLs
    path('', include(router.urls)),

    # Include farmer URLs
    path('', include('farmers.urls')),
]
