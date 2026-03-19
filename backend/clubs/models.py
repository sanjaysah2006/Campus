from django.db import models
from users.models import User


class Club(models.Model):

    CATEGORY_CHOICES = (
        ("TECH", "Tech"),
        ("CULTURAL", "Cultural"),
        ("SPORTS", "Sports"),
        ("GENERAL", "General"),
    )

    name = models.CharField(max_length=200)

    description = models.TextField()

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        default="GENERAL"
    )

    image = models.ImageField(
        upload_to="club_images/",
        null=True,
        blank=True
    )

    organizer = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'ORGANIZER'},
        related_name="organized_club"
    )

    approved = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name