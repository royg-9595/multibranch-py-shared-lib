from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.db.models import UniqueConstraint

class Organization(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Role(models.Model):
    name = models.CharField(max_length=50, unique=False)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey( Organization, on_delete=models.CASCADE, related_name="roles")

    class Meta:
        constraints = [
            UniqueConstraint(fields=['organization', 'name'], name='unique_role_per_organization')
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

class CustomUser(AbstractUser):
    organization = models.ForeignKey( Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    role = models.ForeignKey( Role, on_delete=models.SET_NULL, null=True, blank=True )
    is_org_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    def clean(self):
        # Ensure the user's role belongs to the same organization
        if self.role and self.organization and self.role.organization != self.organization:
            raise ValidationError("The selected role does not belong to the user's organization.")

