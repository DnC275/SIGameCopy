from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth import authenticate

from .models import *


class PlayerSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ['email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

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
    email = serializers.EmailField(max_length=64)

    class Meta:
        model = Player
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['username']
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

        return attrs


class RoomSerializer(ModelSerializer):
    admin = PlayerSerializer(read_only=True)
    # admin_id = serializers.IntegerField()

    class Meta:
        model = Room
        fields = ['name', 'password', 'admin']
        # read_only_fields = ['admin']
        # fields = ['name', 'password', 'admin_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # admin_id = validated_data.pop('admin_id')
        room = super().create(validated_data)
        password = validated_data['password']
        room.set_password(password)
        # room.admin = Player.objects.get(id=admin_id)
        # room.save(update_fields=['password', 'admin'])
        room.save(update_fields=['password'])

        return room


# class LoginToRoomSerializer(ModelSerializer):
#     class Meta:
#         model = Room
#         fields = ['id', 'password']
#
#     def validate(self, attrs):
