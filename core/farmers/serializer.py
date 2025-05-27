from rest_framework import serializers
from .models import Farmer

# Add your serializers here 

class FarmerSerializer(serializers.ModelSerializer):
    # Add calculated CO2 emissions fields
    fertilizer_co2_emissions = serializers.SerializerMethodField()
    pesticide_co2_emissions = serializers.SerializerMethodField()
    energy_co2_emissions = serializers.SerializerMethodField()
    irrigation_co2_emissions = serializers.SerializerMethodField()
    total_co2_emissions = serializers.SerializerMethodField()

    class Meta:
        model = Farmer
        fields = '__all__'

    def get_fertilizer_co2_emissions(self, obj):
        return str(obj.fertilizer_co2_emissions)

    def get_pesticide_co2_emissions(self, obj):
        return str(obj.pesticide_co2_emissions)

    def get_energy_co2_emissions(self, obj):
        return str(obj.energy_co2_emissions)

    def get_irrigation_co2_emissions(self, obj):
        return str(obj.irrigation_co2_emissions)

    def get_total_co2_emissions(self, obj):
        return str(obj.total_co2_emissions) 