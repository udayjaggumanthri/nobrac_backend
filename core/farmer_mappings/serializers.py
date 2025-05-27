from rest_framework import serializers
from .models import FarmerMapping
from farmers.serializer import FarmerSerializer
from companies.serializers import CompanySerializer

class FarmerMappingSerializer(serializers.ModelSerializer):
    farmer_details = FarmerSerializer(source='farmer', read_only=True)
    company_details = CompanySerializer(source='company', read_only=True)

    class Meta:
        model = FarmerMapping
        fields = ['id', 'farmer', 'farmer_details', 'company', 'company_details', 
                 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate that the farmer and company combination is unique
        """
        if FarmerMapping.objects.filter(
            farmer=data['farmer'],
            company=data['company']
        ).exists():
            raise serializers.ValidationError(
                "A mapping between this farmer and company already exists."
            )
        return data

class BulkFarmerMappingSerializer(serializers.Serializer):
    """
    Serializer for creating multiple mappings at once
    """
    company_id = serializers.CharField()
    farmer_ids = serializers.ListField(
        child=serializers.CharField()
    )
    status = serializers.ChoiceField(
        choices=FarmerMapping._meta.get_field('status').choices,
        default='pending'
    )
    notes = serializers.CharField(required=False, allow_blank=True) 