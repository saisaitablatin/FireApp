from django.db import models


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FireLocation(BaseModel):
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.country


class FireIncident(BaseModel):
    date_time = models.DateTimeField()
    severity_level = models.CharField(max_length=50)
    location = models.ForeignKey(FireLocation, on_delete=models.CASCADE)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    def __str__(self):
        return f"{self.date_time} - {self.severity_level}"


class FireStation(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    location = models.ForeignKey(
        FireLocation, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name
