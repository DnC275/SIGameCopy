from datetime import datetime

import jwt
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.conf import settings
from django.contrib.auth.hashers import (
    check_password, make_password,
)
from core.players.models import Player


# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    password = models.CharField('password', max_length=128)
    admin = models.ForeignKey(Player, related_name='administration_room', db_index=True, on_delete=models.CASCADE, null=True)
    # TODO !!! uncomment !!!
    # admin = models.OneToOneField(Player, related_name='administration_room', on_delete=models.CASCADE, db_index=True,
    #                              null=False)
    # presenter = models.OneToOneField(Player, related_name='presentation_room', on_delete=models.SET_NULL, null=True)
    has_access = models.ManyToManyField(Player, related_name='accessible_rooms')
    members = models.ManyToManyField(Player, related_name='current_room')
    # pack = models.ForeignKey('Pack', on_delete=models.)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        # self._password = raw_password

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            # self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    @classmethod
    def get_all_room_names(cls):
        return list(Room.objects.all())
