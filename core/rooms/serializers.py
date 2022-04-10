from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from django.contrib.auth import authenticate
from django.db import transaction

from .models import *
from core.players.serializers import PlayerSerializer, PlayerShortSerializer


class RoomSerializer(ModelSerializer):
    admin = PlayerSerializer(read_only=True)
    has_access = PlayerSerializer(read_only=True, many=True)
    # admin_id = serializers.IntegerField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'password', 'admin', 'has_access']
        # read_only_fields = ['admin']
        # fields = ['name', 'password', 'admin_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # admin_id = validated_data.pop('admin_id')
        with transaction.atomic():
            room = super().create(validated_data)
            password = validated_data['password']
            room.set_password(password)
            # room.admin = Player.objects.get(id=admin_id)
            # room.save(update_fields=['password', 'admin'])
            room.save(update_fields=['password'])

        return room


class RoomShortSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']


class LoginToRoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ['password']

    def validate(self, attrs):
        password = attrs['password']
        room = Room.objects.get(pk=self.context['view'].kwargs['pk'])

        if not room.check_password(password):
            raise PermissionDenied('Incorrect password')

        attrs['room'] = room
        return attrs