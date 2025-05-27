from django.urls import path, include
from .views import (
    FarmerViewSet,
    FarmerMediaUploadView,
    FarmerEmissionsView
)

# Create a router and register our viewsets with it
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'farmers', FarmerViewSet)

urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Additional farmer-specific endpoints
    path('farmers/<uuid:farmer_id>/emissions/', FarmerEmissionsView.as_view({'get': 'retrieve'}), name='farmer-emissions'),
    path('farmers/media/upload/', FarmerMediaUploadView.as_view({'post': 'create'}), name='farmer-media-upload'),
] 