from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth import authenticate

from .models import Player


class PlayerSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ['email', 'username', 'password']
        write_only_fields = ['password']

    def create(self, validated_data):
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
    email = serializers.EmailField(write_only=True, max_length=64)

    class Meta:
        model = Player
        fields = ['email', 'password']
        write_only_fields = ['password']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        player = authenticate(request=self.context.get('request'), email=email, password=password)

        if not player:
            msg = 'Unable to log in with provided credentials.'
            raise NotAuthenticated(msg, 'authorization')

        del attrs['email']
        del attrs['password']

        attrs['player'] = player
        return attrs
