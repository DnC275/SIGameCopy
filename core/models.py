from datetime import datetime

import jwt
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.conf import settings
from django.contrib.auth.hashers import (
    check_password, make_password,
)


class PlayerManager(BaseUserManager):
    """
    Custom player model manager where username is the unique identifiers
    for authentication.
    """

    def create_user(self, email, username, password, **extra_fields):
        """
        Create and save a Player with the given email and password.
        """
        # if not email:
        #     raise ValueError('The Email must be set')
        # email = self.normalize_email(email)
        player = self.model(username=username, email=email, **extra_fields)
        player.set_password(password)
        player.save()
        return player

    def create_superuser(self, email, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email=email, username=username, password=password, **extra_fields)


class Player(AbstractUser):
    email = models.EmailField('email', db_index=True, max_length=64, unique=True)
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)
    # current_room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = PlayerManager()

    def generate_jwt_token(self):
        token = jwt.encode({
            'id': self.pk
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    # @classmethod
    # def resolve_jwt(cls, token) -> dict:
    #     payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms='HS256')
    #     return payload

    @classmethod
    def get_by_jwt(cls, token):
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms='HS256')

        if 'id' not in payload:
            return None

        return cls.objects.get(id=payload['id'])


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


class Pack(models.Model):
    pass
