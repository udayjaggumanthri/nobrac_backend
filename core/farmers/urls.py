from django.urls import path, include
from .views import (
    FarmerViewSet,
    FarmerMediaUploadView,
    FarmerEmissionsView,
    FarmerSyncView
)

# Create a router and register our viewsets with it
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
# Registering with an empty prefix '' makes this the base for /api/farmers/
# basename is required for empty prefix with ModelViewSet
router.register(r'', FarmerViewSet, basename='farmer')

urlpatterns = [
    # Specific paths should come before the general router inclusion
    # Paths are now relative to /api/farmers/
    path('sync/', FarmerSyncView.as_view(), name='farmer-sync'),
    path('media/upload/', FarmerMediaUploadView.as_view({'post': 'create'}), name='farmer-media-upload'),
    path('<str:farmer_id>/emissions/', FarmerEmissionsView.as_view({'get': 'retrieve'}), name='farmer-emissions'),

    # Include the router URLs (handles /api/farmers/ and /api/farmers/<id>/ for FarmerViewSet)
    path('', include(router.urls)),
]