from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Farmer
from .serializer import FarmerSerializer
from rest_framework import generics, viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes, action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from datetime import datetime


# Generics
class FarmerList(generics.ListCreateAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer


class FarmerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    lookup_field = 'pk'


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_media(request):
    """
    Handle file uploads from the React Native app
    """
    try:
        # Check if a file was uploaded
        if 'file' not in request.FILES:
            return Response({'error': 'No file found'}, status=400)

        file = request.FILES['file']
        farmer_id = request.data.get('farmer_id')
        media_type = request.data.get('media_type')

        if not farmer_id:
            return Response({'error': 'No farmer ID provided'}, status=400)

        # Create directory if it doesn't exist
        directory = f'media/farmers/{farmer_id}'
        os.makedirs(directory, exist_ok=True)

        # Save the file
        file_name = f"{media_type}_{file.name}" if media_type else file.name
        path = f'{directory}/{file_name}'
        default_storage.save(path, ContentFile(file.read()))

        # Return the file URL
        file_url = f'/media/farmers/{farmer_id}/{file_name}'

        return Response({
            'success': True,
            'file_url': file_url,
        })
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def farmer_emissions(request, pk):
    """
    Get CO2 emissions data for a specific farmer
    """
    try:
        farmer = get_object_or_404(Farmer, pk=pk)

        emissions_data = {
            'fertilizer_co2_emissions': str(farmer.fertilizer_co2_emissions),
            'pesticide_co2_emissions': str(farmer.pesticide_co2_emissions),
            'energy_co2_emissions': str(farmer.energy_co2_emissions),
            'irrigation_co2_emissions': str(farmer.irrigation_co2_emissions),
            'total_co2_emissions': str(farmer.total_co2_emissions),
            'farmer_id': farmer.id,
            'farmer_name': farmer.farmer_name
        }

        return Response(emissions_data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


class FarmerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing farmer instances.
    """
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Optionally restricts the returned farmers by filtering against
        query parameters in the URL.
        """
        queryset = Farmer.objects.all()
        name = self.request.query_params.get('name', None)
        village = self.request.query_params.get('village', None)
        district = self.request.query_params.get('district', None)

        if name is not None:
            queryset = queryset.filter(farmer_name__icontains=name)
        if village is not None:
            queryset = queryset.filter(village__icontains=village)
        if district is not None:
            queryset = queryset.filter(district__icontains=district)

        return queryset


class FarmerMediaUploadView(viewsets.ViewSet):
    """
    ViewSet for handling farmer media uploads.
    """
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request):
        """
        Handle media file upload for a farmer.
        """
        file = request.FILES.get('file')
        farmer_id = request.data.get('farmer_id')
        media_type = request.data.get('media_type', 'photo')

        if not file or not farmer_id:
            return Response(
                {'error': 'File and farmer_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            farmer = Farmer.objects.get(id=farmer_id)
            
            # Handle different media types
            if media_type == 'photo':
                farmer.farmer_photo = file
            elif media_type == 'land_photo_1':
                farmer.land_photo_1 = file
            elif media_type == 'land_photo_2':
                farmer.land_photo_2 = file
            elif media_type == 'land_photo_3':
                farmer.land_photo_3 = file
            elif media_type == 'land_photo_4':
                farmer.land_photo_4 = file
            elif media_type == 'soil_characteristics':
                farmer.soil_characteristics = file
            elif media_type == 'fertilizer_photos':
                farmer.fertilizer_photos = file
            elif media_type == 'crop_protection_photos':
                farmer.crop_protection_photos = file
            else:
                return Response(
                    {'error': 'Invalid media type'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            farmer.save()
            return Response({
                'success': True,
                'file_url': getattr(farmer, f'{media_type}').url
            })

        except Farmer.DoesNotExist:
            return Response(
                {'error': 'Farmer not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class FarmerEmissionsView(viewsets.ViewSet):
    """
    ViewSet for calculating and retrieving farmer emissions data.
    """
    def retrieve(self, request, farmer_id=None):
        """
        Calculate and return emissions data for a specific farmer.
        """
        farmer = get_object_or_404(Farmer, id=farmer_id)
        
        # Calculate fertilizer emissions (kg CO2e)
        fertilizer_emissions = 0.0
        if farmer.fertilizer_type and farmer.application_rate:
            # Conversion factors for different fertilizer types
            fertilizer_factors = {
                'NPK': 4.5,  # kg CO2e per kg of NPK
                'Urea': 2.1,  # kg CO2e per kg of Urea
                'DAP': 1.2,  # kg CO2e per kg of DAP
                'MOP': 0.6,  # kg CO2e per kg of MOP
            }
            factor = fertilizer_factors.get(farmer.fertilizer_type, 2.0)  # default factor
            fertilizer_emissions = float(farmer.application_rate) * factor

        # Calculate pesticide emissions (kg CO2e)
        pesticide_emissions = 0.0
        if farmer.pesticide_category and farmer.pesticide_application_rate:
            # Conversion factors for different pesticide categories
            pesticide_factors = {
                'Insecticide': 5.2,  # kg CO2e per kg of insecticide
                'Fungicide': 3.8,    # kg CO2e per kg of fungicide
                'Herbicide': 4.1,    # kg CO2e per kg of herbicide
            }
            factor = pesticide_factors.get(farmer.pesticide_category, 4.0)  # default factor
            pesticide_emissions = float(farmer.pesticide_application_rate) * factor

        # Calculate energy emissions (kg CO2e)
        energy_emissions = 0.0
        if farmer.energy_used and farmer.energy_category:
            # Conversion factors for different energy sources
            energy_factors = {
                'Electricity': 0.82,  # kg CO2e per kWh
                'Diesel': 2.68,       # kg CO2e per liter
                'Petrol': 2.31,       # kg CO2e per liter
            }
            factor = energy_factors.get(farmer.energy_category, 1.0)  # default factor
            energy_emissions = float(farmer.energy_used) * factor

        # Calculate irrigation emissions (kg CO2e)
        irrigation_emissions = 0.0
        if farmer.power_consumption and farmer.power_source:
            # Conversion factors for different power sources
            power_factors = {
                'Electric': 0.82,  # kg CO2e per kWh
                'Diesel': 2.68,    # kg CO2e per liter
                'Solar': 0.0,      # kg CO2e per kWh (renewable)
            }
            factor = power_factors.get(farmer.power_source, 1.0)  # default factor
            irrigation_emissions = float(farmer.power_consumption) * factor

        # Calculate total emissions
        total_emissions = (
            fertilizer_emissions +
            pesticide_emissions +
            energy_emissions +
            irrigation_emissions
        )

        emissions_data = {
            'fertilizer_co2_emissions': round(fertilizer_emissions, 2),
            'pesticide_co2_emissions': round(pesticide_emissions, 2),
            'energy_co2_emissions': round(energy_emissions, 2),
            'irrigation_co2_emissions': round(irrigation_emissions, 2),
            'total_co2_emissions': round(total_emissions, 2),
            'farmer_id': str(farmer.id),
            'farmer_name': farmer.farmer_name,
            'calculation_date': datetime.now().isoformat(),
            'emissions_unit': 'kg CO2e',
            'land_area': farmer.acreage,
            'land_area_unit': 'acres'
        }
        
        return Response(emissions_data) 