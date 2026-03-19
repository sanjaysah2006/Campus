from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('ORGANIZER', 'Organizer'),
        ('STUDENT', 'Student'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


class StudentProfile(models.Model):

    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    name = models.CharField(max_length=150)

    roll_no = models.CharField(max_length=20, unique=True)

    course = models.CharField(max_length=100,null=True, blank=True)

    batch = models.CharField(max_length=20,null=True, blank=True)

    semester = models.IntegerField(null=True, blank=True)

    section = models.CharField(max_length=10)

    phone = models.CharField(max_length=15)

    id_card = models.ImageField(
        upload_to="student_ids/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.roll_no} - {self.name}"