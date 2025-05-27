from django.contrib import admin
from .models import Farmer

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('farmer_name', 'mobile', 'village', 'district', 'state', 'created_at', 'sync_status')
    list_filter = ('sync_status', 'district', 'state', 'gender')
    search_fields = ('farmer_name', 'mobile', 'govt_id', 'village', 'district')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('farmer_name', 'spouse_name', 'gender', 'mobile', 'alt_mobile', 'govt_id')
        }),
        ('Location', {
            'fields': ('village', 'mandal', 'district', 'state', 'pincode')
        }),
        ('Land Information', {
            'fields': ('acreage', 'land_status', 'product_ids')
        }),
        ('Organization', {
            'fields': ('has_organization', 'fpo_name', 'fpg_name', 'fpg_id')
        }),
        ('Social Information', {
            'fields': ('category', 'literacy', 'children', 'livelihood', 'annual_income', 
                      'other_source_income', 'total_income')
        }),
        ('Crop Information', {
            'fields': ('crop_name', 'crop_area', 'crop_area_unit', 'yield_produced', 
                      'yield_unit', 'cropping_season', 'cropping_pattern', 
                      'farming_practice', 'agriculture_crop_type')
        }),
        ('Soil Characteristics', {
            'fields': ('soil_type', 'soil_ph', 'ec', 'ec_unit', 'organic_carbon', 'organic_carbon_unit')
        }),
        ('Fertilizer', {
            'fields': ('fertilizer_type', 'application_rate', 'application_rate_unit')
        }),
        ('Crop Protection', {
            'fields': ('pesticide_category', 'pesticide_application_rate', 'pesticide_application_rate_unit')
        }),
        ('Fuel & Energy', {
            'fields': ('direct_energy_use', 'energy_used', 'energy_unit', 'energy_category')
        }),
        ('Irrigation', {
            'fields': ('water_source', 'irrigation_method', 'power_source', 
                      'power_consumption', 'power_consumption_unit')
        }),
        ('Transport', {
            'fields': ('transport_activity_type', 'transport_mode', 'distance', 
                      'distance_unit', 'fuel_type', 'fuel_consumption', 'fuel_consumption_unit')
        }),
        ('Media', {
            'fields': ('farmer_photo', 'land_photo_1', 'land_photo_2', 'land_photo_3', 
                      'land_photo_4', 'soil_characteristics', 'fertilizer_photos', 
                      'crop_protection_photos')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'sync_status', 'is_read_only'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_read_only:
            return self.readonly_fields + ('farmer_name', 'mobile', 'govt_id')
        return self.readonly_fields 