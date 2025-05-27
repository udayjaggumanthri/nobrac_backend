from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import FarmerMapping
from .serializers import FarmerMappingSerializer, BulkFarmerMappingSerializer
from farmers.models import Farmer
from companies.models import Company
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError

class FarmerMappingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing farmer-company mappings
    """
    queryset = FarmerMapping.objects.all()
    serializer_class = FarmerMappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter mappings by farmer or company
        """
        queryset = FarmerMapping.objects.all()
        farmer_id = self.request.query_params.get('farmer', None)
        company_id = self.request.query_params.get('company', None)
        status = self.request.query_params.get('status', None)

        if farmer_id:
            queryset = queryset.filter(farmer_id=farmer_id)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple mappings at once
        """
        serializer = BulkFarmerMappingSerializer(data=request.data)
        if serializer.is_valid():
            company_id = serializer.validated_data['company_id']
            farmer_ids = serializer.validated_data['farmer_ids']
            status_value = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')

            # Get the company
            company = get_object_or_404(Company, id=company_id)

            # Create mappings
            created_mappings = []
            duplicate_mappings = []
            failed_mappings = []

            for farmer_id in farmer_ids:
                try:
                    farmer = get_object_or_404(Farmer, id=farmer_id)
                    
                    # Check if mapping already exists
                    existing_mapping = FarmerMapping.objects.filter(
                        farmer=farmer,
                        company=company
                    ).first()
                    
                    if existing_mapping:
                        duplicate_mappings.append({
                            'farmer_id': farmer_id,
                            'farmer_name': farmer.farmer_name,
                            'existing_status': existing_mapping.status
                        })
                        continue

                    # Create new mapping
                    mapping = FarmerMapping.objects.create(
                        farmer=farmer,
                        company=company,
                        status=status_value,
                        notes=notes
                    )
                    created_mappings.append(mapping)
                except IntegrityError:
                    duplicate_mappings.append({
                        'farmer_id': farmer_id,
                        'farmer_name': farmer.farmer_name if 'farmer' in locals() else 'Unknown',
                        'error': 'Mapping already exists'
                    })
                except Exception as e:
                    failed_mappings.append({
                        'farmer_id': farmer_id,
                        'error': str(e)
                    })

            # Prepare response data
            response_data = {
                'created': FarmerMappingSerializer(created_mappings, many=True).data,
                'duplicates': duplicate_mappings,
                'failed': failed_mappings,
                'summary': {
                    'total': len(farmer_ids),
                    'created': len(created_mappings),
                    'duplicates': len(duplicate_mappings),
                    'failed': len(failed_mappings)
                }
            }

            # Return appropriate status code based on results
            if created_mappings:
                return Response(response_data, status=status.HTTP_201_CREATED)
            elif duplicate_mappings:
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of a mapping
        """
        mapping = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(FarmerMapping._meta.get_field('status').choices):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        mapping.status = new_status
        mapping.notes = request.data.get('notes', mapping.notes)
        mapping.save()

        return Response(FarmerMappingSerializer(mapping).data)
