from django.db import models
from django.core.validators import RegexValidator
import uuid
from decimal import Decimal

def farmer_photo_path(instance, filename):
    return f'farmers/{instance.id}/profile/{filename}'

def land_photo_path(instance, filename):
    return f'farmers/{instance.id}/land/{filename}'

def land_image_path(instance, filename):
    return f'farmers/{instance.id}/land_image/{filename}'

def soil_characteristics_path(instance, filename):
    return f'farmers/{instance.id}/soil/{filename}'

def fertilizer_photos_path(instance, filename):
    return f'farmers/{instance.id}/fertilizer/{filename}'

def crop_protection_photos_path(instance, filename):
    return f'farmers/{instance.id}/crop_protection/{filename}'

class Farmer(models.Model):
    SYNC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('failed', 'Failed'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    # Primary and System Fields
    id = models.CharField(max_length=36, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=10, choices=SYNC_STATUS_CHOICES, default='pending')
    is_read_only = models.BooleanField(default=False)

    # Farmer Information
    farmer_name = models.CharField(max_length=100)
    spouse_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    mobile = models.CharField(max_length=15, validators=[RegexValidator(r'^[0-9]{10}$')], null=True, blank=True)
    alt_mobile = models.CharField(max_length=15, validators=[RegexValidator(r'^[0-9]{10}$')], null=True, blank=True)
    govt_id = models.CharField(max_length=50, null=True, blank=True)

    # Land Information
    acreage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    land_status = models.CharField(max_length=50, null=True, blank=True)
    product_ids = models.TextField(null=True, blank=True)

    # Location Information
    village = models.CharField(max_length=100, null=True, blank=True)
    mandal = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=10, validators=[RegexValidator(r'^[0-9]{6}$')], null=True, blank=True)

    # Organization Information
    has_organization = models.BooleanField(default=False)
    fpo_name = models.CharField(max_length=100, null=True, blank=True)
    fpg_name = models.CharField(max_length=100, null=True, blank=True)
    fpg_id = models.CharField(max_length=50, null=True, blank=True)

    # Social Information
    category = models.CharField(max_length=100, null=True, blank=True)
    literacy = models.CharField(max_length=100, null=True, blank=True)
    children = models.CharField(max_length=50, null=True, blank=True)
    livelihood = models.CharField(max_length=100, null=True, blank=True)
    annual_income = models.CharField(max_length=100, null=True, blank=True)
    other_source_income = models.CharField(max_length=100, null=True, blank=True)
    total_income = models.CharField(max_length=100, null=True, blank=True)

    # Crop Information
    crop_name = models.CharField(max_length=100, null=True, blank=True)
    crop_area = models.CharField(max_length=100, null=True, blank=True)
    crop_area_unit = models.CharField(max_length=10, null=True, blank=True)
    yield_produced = models.CharField(max_length=100, null=True, blank=True)
    yield_unit = models.CharField(max_length=10, null=True, blank=True)
    cropping_season = models.CharField(max_length=100, null=True, blank=True)
    cropping_pattern = models.CharField(max_length=100, null=True, blank=True)
    farming_practice = models.CharField(max_length=100, null=True, blank=True)
    agriculture_crop_type = models.CharField(max_length=100, null=True, blank=True)

    # Soil Characteristics
    soil_type = models.CharField(max_length=100, null=True, blank=True)
    soil_ph = models.CharField(max_length=20, null=True, blank=True)
    ec = models.CharField(max_length=20, null=True, blank=True)
    ec_unit = models.CharField(max_length=10, null=True, blank=True)
    organic_carbon = models.CharField(max_length=20, null=True, blank=True)
    organic_carbon_unit = models.CharField(max_length=10, null=True, blank=True)

    # Fertilizer
    fertilizer_type = models.CharField(max_length=100, null=True, blank=True)
    application_rate = models.CharField(max_length=50, null=True, blank=True)
    application_rate_unit = models.CharField(max_length=20, null=True, blank=True)

    # Crop Protection
    pesticide_category = models.CharField(max_length=100, null=True, blank=True)
    pesticide_application_rate = models.CharField(max_length=50, null=True, blank=True)
    pesticide_application_rate_unit = models.CharField(max_length=20, null=True, blank=True)

    # Fuel & Energy
    direct_energy_use = models.CharField(max_length=100, null=True, blank=True)
    energy_used = models.CharField(max_length=50, null=True, blank=True)
    energy_unit = models.CharField(max_length=10, null=True, blank=True)
    energy_category = models.CharField(max_length=50, null=True, blank=True)

    # Irrigation
    water_source = models.CharField(max_length=100, null=True, blank=True)
    irrigation_method = models.CharField(max_length=100, null=True, blank=True)
    power_source = models.CharField(max_length=100, null=True, blank=True)
    power_consumption = models.CharField(max_length=50, null=True, blank=True)
    power_consumption_unit = models.CharField(max_length=10, null=True, blank=True)

    # Transport
    transport_activity_type = models.CharField(max_length=100, null=True, blank=True)
    transport_mode = models.CharField(max_length=100, null=True, blank=True)
    distance = models.CharField(max_length=50, null=True, blank=True)
    distance_unit = models.CharField(max_length=10, null=True, blank=True)
    fuel_type = models.CharField(max_length=50, null=True, blank=True)
    fuel_consumption = models.CharField(max_length=50, null=True, blank=True)
    fuel_consumption_unit = models.CharField(max_length=10, null=True, blank=True)

    # Media Paths
    farmer_photo = models.ImageField(upload_to=farmer_photo_path, null=True, blank=True)
    land_photo_1 = models.ImageField(upload_to=land_photo_path, null=True, blank=True)
    land_photo_2 = models.ImageField(upload_to=land_photo_path, null=True, blank=True)
    land_photo_3 = models.ImageField(upload_to=land_photo_path, null=True, blank=True)
    land_photo_4 = models.ImageField(upload_to=land_photo_path, null=True, blank=True)
    soil_characteristics = models.ImageField(upload_to=soil_characteristics_path, null=True, blank=True)
    fertilizer_photos = models.ImageField(upload_to=fertilizer_photos_path, null=True, blank=True)
    crop_protection_photos = models.ImageField(upload_to=crop_protection_photos_path, null=True, blank=True)

    class Meta:
        db_table = 'farmers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['farmer_name']),
            models.Index(fields=['mobile']),
            models.Index(fields=['govt_id']),
            models.Index(fields=['district']),
            models.Index(fields=['state']),
            models.Index(fields=['sync_status']),
        ]

    def __str__(self):
        return self.farmer_name or str(self.id)

    # Helper function to safely convert string to decimal
    def safe_decimal(self, value):
        try:
            return Decimal(value) if value else Decimal('0')
        except (ValueError, TypeError):
            return Decimal('0')

    @property
    def fertilizer_co2_emissions(self):
        """Calculate fertilizer CO2 emissions"""
        if not self.fertilizer_type or not self.application_rate:
            return Decimal('0')

        application_rate = self.safe_decimal(self.application_rate)
        fertilizer_type = self.fertilizer_type.strip().lower() if self.fertilizer_type else ''

        if 'n' in fertilizer_type and 'application' in fertilizer_type:
            return (application_rate * Decimal('0.1')) / Decimal('1000')
        elif ('p' in fertilizer_type or 'k' in fertilizer_type) and 'application' in fertilizer_type:
            return (application_rate * Decimal('0.2')) / Decimal('1000')
        elif 'organic' in fertilizer_type:
            return (application_rate * Decimal('0.6')) / Decimal('1000')

        return Decimal('0')

    @property
    def pesticide_co2_emissions(self):
        """Calculate pesticide CO2 emissions"""
        if not self.pesticide_category or not self.pesticide_application_rate:
            return Decimal('0')

        pesticide_rate = self.safe_decimal(self.pesticide_application_rate)
        pesticide_category = self.pesticide_category.strip().lower() if self.pesticide_category else ''

        if 'pesticide' in pesticide_category:
            return (pesticide_rate * Decimal('5.1')) / Decimal('1000')
        elif 'fungicide' in pesticide_category:
            return (pesticide_rate * Decimal('6.3')) / Decimal('1000')

        return Decimal('0')

    @property
    def energy_co2_emissions(self):
        """Calculate energy CO2 emissions"""
        if not self.direct_energy_use or not self.energy_used:
            return Decimal('0')

        energy_used = self.safe_decimal(self.energy_used)
        energy_type = self.direct_energy_use.strip().lower() if self.direct_energy_use else ''

        if 'fuelwood' in energy_type:
            return (energy_used * Decimal('1.8')) / Decimal('1000')
        elif 'coal' in energy_type:
            return (energy_used * Decimal('2.5')) / Decimal('1000')
        elif 'petrol' in energy_type:
            return (energy_used * Decimal('2.3')) / Decimal('1000')
        elif 'diesel' in energy_type:
            return (energy_used * Decimal('2.68')) / Decimal('1000')
        elif 'electricity' in energy_type or 'grid' in energy_type:
            return (energy_used * Decimal('0.8')) / Decimal('1000')

        return Decimal('0')

    @property
    def irrigation_co2_emissions(self):
        """Calculate irrigation CO2 emissions"""
        if not self.power_source or not self.power_consumption:
            return Decimal('0')

        power_consumption = self.safe_decimal(self.power_consumption)
        power_type = self.power_source.strip().lower() if self.power_source else ''

        if 'fuelwood' in power_type:
            return (power_consumption * Decimal('1.8')) / Decimal('1000')
        elif 'coal' in power_type:
            return (power_consumption * Decimal('2.5')) / Decimal('1000')
        elif 'petrol' in power_type:
            return (power_consumption * Decimal('2.3')) / Decimal('1000')
        elif 'diesel' in power_type:
            return (power_consumption * Decimal('2.68')) / Decimal('1000')
        elif 'electricity' in power_type or 'grid' in power_type:
            return (power_consumption * Decimal('0.8')) / Decimal('1000')

        return Decimal('0')

    @property
    def total_co2_emissions(self):
        """Calculate total CO2 emissions"""
        return (
            self.fertilizer_co2_emissions +
            self.pesticide_co2_emissions +
            self.energy_co2_emissions +
            self.irrigation_co2_emissions
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())

        super().save(*args, **kwargs)

