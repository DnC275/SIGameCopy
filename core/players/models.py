import jwt
import uuid
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.conf import settings
from django.db.models import signals
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password


# Create your models here.
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
    is_verified = models.BooleanField('verified', default=False)
    verification_uuid = models.UUIDField('Unique Verification UUID', default=uuid.uuid4)
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

    @property
    def current_room_id(self):
        if len(self.current_room.all()) > 0:
            return self.current_room.all()[0].id
        return None


def user_post_save(sender, instance, signal, *args, **kwargs):
    if not instance.is_verified:
        # Send verification email
        from django.core.mail import EmailMultiAlternatives

        subject, from_email, to = 'Svoyak verify', 'no-reply.svoyak@yandex.ru', instance.email
        html_content = f"<a href=https://jolly-morse-6d6dc0.netlify.app/registration_verify/?id={instance.verification_uuid)}> Thanks for reginstration on Svoyak! Please follow the link to verify your account</a>"
        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.content_subtype = "html"
        print(1)
        msg.send()


signals.post_save.connect(user_post_save, sender=Player)
