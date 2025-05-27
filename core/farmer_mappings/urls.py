from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmerMappingViewSet

router = DefaultRouter()
router.register(r'mappings', FarmerMappingViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 