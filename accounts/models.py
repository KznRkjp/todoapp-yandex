
from django.contrib.auth.models import User
from django.db import models




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField(blank=True, null=True)
    trello_key = models.CharField(max_length=32, null=True, blank=True)
    trello_token = models.CharField(max_length=64, null=True, blank=True)
    hrennn = False
    def __str__(self):
        return "Профиль пользователя %s" % self.user.username
