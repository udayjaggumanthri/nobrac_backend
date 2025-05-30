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
from rest_framework.views import APIView


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

    def create(self, request, *args, **kwargs):
        print("Incoming data for create:", request.data)  # Log incoming data
        response = super().create(request, *args, **kwargs)
        print("Response data for create:", response.data)  # Log response data
        return response

    def update(self, request, *args, **kwargs):
        # Ensure 'id' is not part of the request data for updates
        if 'id' in request.data:
            print(f"Warning: 'id' field found in update request data for ID {kwargs.get('id')}. Removing it.")
            # Create a mutable copy if QueryDict
            if hasattr(request.data, '_mutable'):
                request.data._mutable = True
                request.data.pop('id', None)
                request.data._mutable = False
            elif isinstance(request.data, dict):
                 request.data.pop('id', None)

        print(f"Incoming data for update (ID: {kwargs.get('id')}):", request.data)
        response = super().update(request, *args, **kwargs)
        print(f"Response data for update (ID: {kwargs.get('id')}):", response.data)
        return response

    def partial_update(self, request, *args, **kwargs):
        # Ensure 'id' is not part of the request data for partial updates
        if 'id' in request.data:
            print(f"Warning: 'id' field found in partial_update request data for ID {kwargs.get('id')}. Removing it.")
            if hasattr(request.data, '_mutable'):
                request.data._mutable = True
                request.data.pop('id', None)
                request.data._mutable = False
            elif isinstance(request.data, dict):
                request.data.pop('id', None)

        print(f"Incoming data for partial_update (ID: {kwargs.get('id')}):", request.data)
        response = super().partial_update(request, *args, **kwargs)
        print(f"Response data for partial_update (ID: {kwargs.get('id')}):", response.data)
        return response


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
    ViewSet for retrieving farmer emissions data.
    """
    def retrieve(self, request, farmer_id=None):
        """
        Retrieve emissions data for a specific farmer.
        """
        farmer = get_object_or_404(Farmer, id=farmer_id)

        emissions_data = {
            'fertilizer_co2_emissions': str(farmer.fertilizer_co2_emissions),
            'pesticide_co2_emissions': str(farmer.pesticide_co2_emissions),
            'energy_co2_emissions': str(farmer.energy_co2_emissions),
            'irrigation_co2_emissions': str(farmer.irrigation_co2_emissions),
            'total_co2_emissions': str(farmer.total_co2_emissions),
            'farmer_id': str(farmer.id),
            'farmer_name': farmer.farmer_name,
            'calculation_date': datetime.now().isoformat(),
            'emissions_unit': 'kg CO2e',
            'land_area': farmer.acreage,
            'land_area_unit': 'acres'
        }
        
        return Response(emissions_data)


class FarmerSyncView(APIView):
    def post(self, request):
        try:
            farmers_data = request.data
            if not isinstance(farmers_data, list):
                return Response({"error": "Expected a list of farmer objects"}, status=status.HTTP_400_BAD_REQUEST)

            saved_farmers_data = []
            error_details = []
            success_count = 0
            failure_count = 0

            for farmer_item in farmers_data:
                farmer_id = farmer_item.get('id')
                if not farmer_id:
                    error_details.append({"detail": "Missing 'id' in farmer data object.", "data": farmer_item})
                    failure_count += 1
                    continue

                try:
                    instance = Farmer.objects.get(id=farmer_id)
                    serializer = FarmerSerializer(instance, data=farmer_item, partial=True) # partial=True for updates
                except Farmer.DoesNotExist:
                    serializer = FarmerSerializer(data=farmer_item)
                
                if serializer.is_valid():
                    try:
                        saved_farmer = serializer.save()
                        saved_farmers_data.append(FarmerSerializer(saved_farmer).data) # Use fresh serializer for response data
                        success_count += 1
                    except Exception as e_save:
                        error_details.append({"id": farmer_id, "errors": str(e_save)})
                        failure_count += 1
                else:
                    error_details.append({"id": farmer_id, "errors": serializer.errors})
                    failure_count += 1
            
            response_status = status.HTTP_207_MULTI_STATUS if failure_count > 0 and success_count > 0 else \
                              status.HTTP_201_CREATED if success_count > 0 else \
                              status.HTTP_400_BAD_REQUEST

            return Response({
                "message": f"{success_count} farmers synced successfully, {failure_count} failed.",
                "saved_farmers": saved_farmers_data,
                "errors": error_details if error_details else None
            }, status=response_status)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e), "detail": "An unexpected error occurred during sync."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)