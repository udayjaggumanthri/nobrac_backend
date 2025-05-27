from django.contrib import admin
from .models import FarmerMapping

@admin.register(FarmerMapping)
class FarmerMappingAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'company', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('farmer__farmer_name', 'company__name', 'notes')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Mapping Information', {
            'fields': ('farmer', 'company', 'status', 'notes')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('farmer', 'company')
        return self.readonly_fields
