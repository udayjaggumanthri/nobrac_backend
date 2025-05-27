from django.db import models
import uuid
from farmers.models import Farmer
from companies.models import Company
from django.utils import timezone

class FarmerMapping(models.Model):
    """
    Model to store farmer-company mappings
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='company_mappings')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='farmer_mappings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'farmer_mappings'
        ordering = ['-created_at']
        unique_together = ['farmer', 'company']
        indexes = [
            models.Index(fields=['farmer']),
            models.Index(fields=['company']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Farmer-Company Mapping'
        verbose_name_plural = 'Farmer-Company Mappings'

    def __str__(self):
        return f"{self.farmer.farmer_name} - {self.company.name} ({self.status})"

    def save(self, *args, **kwargs):
        # Update the updated_at timestamp
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
