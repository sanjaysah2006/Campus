from django.db import models
from users.models import User
from clubs.models import Club


class Event(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="events"
    )

    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organized_events"
    )

    date = models.DateField()

    location = models.CharField(max_length=200)

    image = models.ImageField(
        upload_to="event_images/",
        null=True,
        blank=True
    )

    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.club.name})"


# ---------------------------------------------
# EVENT INTERACTION (for analytics / tracking)
# ---------------------------------------------
class EventInteraction(models.Model):

    INTERACTION_CHOICES = (
        ('VIEW', 'View'),
        ('SEARCH', 'Search'),
        ('REGISTER', 'Register'),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'}
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="interactions"
    )

    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_CHOICES
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.interaction_type}"


# ---------------------------------------------
# EVENT REGISTRATION
# ---------------------------------------------
class EventRegistration(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'}
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'event')

    def __str__(self):
        return f"{self.student.username} → {self.event.title}"