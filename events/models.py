from django.db import models
from django.conf import settings


class Event(models.Model):
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    location = models.CharField(max_length=300)
    invitees = models.JSONField(default=list)  #list of emails
    attendees = models.JSONField(default=dict)  # going/maybe/not going
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title