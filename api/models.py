from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# 1. User Profile (Role Management)
class Profile(models.Model):
    ROLE_CHOICES = (('seeker', 'Seeker'), ('facilitator', 'Facilitator'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} ({self.role})"

# 2. OTP Store
class EmailOTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at

# 3. Events
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    language = models.CharField(max_length=50, db_index=True)
    location = models.CharField(max_length=255, db_index=True)
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField()
    capacity = models.PositiveIntegerField(null=True, blank=True)
    # The creator is a Facilitator (User)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_events')
    created_at = models.DateTimeField(auto_now_add=True)

# 4. Enrollments (The Link between Seeker and Event)
class Enrollment(models.Model):
    STATUS_CHOICES = (('enrolled', 'Enrolled'), ('canceled', 'Canceled'))
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='enrollments')
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent double enrollment in the DB layer
        unique_together = ('event', 'seeker')