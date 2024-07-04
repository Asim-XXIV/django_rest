from django.db import models
from django.utils import timezone
from datetime import timedelta


class AdminAdvertisement(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField()
    discounts = models.CharField(max_length=255, blank=True, null=True)
    offers = models.CharField(max_length=255, blank=True, null=True)
    referral_code = models.CharField(max_length=50, blank=True, null=True)
    guidelines = models.TextField()
    links = models.CharField(max_length=255, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    is_running = models.BooleanField(default=True)
    duration = models.DurationField(default=timedelta(days=1))  # Default duration of 1 day
    priority = models.PositiveIntegerField(default=1)  # Changed to PositiveIntegerField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()  # Set created_at if it's None

        # Automatically set is_running to False if the ad has expired
        if self.created_at + self.duration < timezone.now():
            self.is_running = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
