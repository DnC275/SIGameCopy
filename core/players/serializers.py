from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from django.contrib.auth import authenticate
from django.db import transaction

from .models import *


class PlayerSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        with transaction.atomic():
            player = super().create(validated_data)
            password = validated_data['password']
            player.set_password(password)
            player.save(update_fields=['password'])

        return player


class PlayerShortSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ['username']


class AuthByEmailPasswordSerializer(ModelSerializer):
    email = serializers.EmailField(max_length=64)

    class Meta:
        model = Player
        fields = ['id', 'username', 'email', 'password', 'current_room_id']
        read_only_fields = ['username', 'current_room_id']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        player = authenticate(request=self.context.get('request'), email=email, password=password)

        if not player:
            msg = 'Unable to log in with provided credentials.'
            raise NotAuthenticated(msg, 'authorization')

        attrs['id'] = player.id
        attrs['username'] = player.username
        attrs['current_room_id'] = player.current_room_id

        return attrs