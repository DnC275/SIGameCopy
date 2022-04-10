import jwt
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.rooms.models import Room
from .serializers import *
from rest_framework.decorators import action
from django.conf import settings
from django.core import serializers as django_serializers
# from django.contrib.auth import get_user_model, authenticate


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    # serializer_class = RoomSerializer

    # def create(self, request, *args, **kwargs):
    #     request.data['admin_id'] = request.user.id
    #     return super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return RoomShortSerializer
        return RoomSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = Player.objects.get(id=request.user.id)
        if (admin.administration_room.exists() or admin.current_room.exists()) and not admin.is_superuser:
            msg = 'Already in game'
            return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(admin=admin, members=[admin])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LoginToRoomView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LoginToRoomSerializer
    # serializer_class = RoomSerializer

    @property
    def allowed_methods(self):
        return ['post']

    def get_serializer_context(self):
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room = serializer.validated_data['room']
        player = Player.objects.get(id=request.user.id)
        if player.current_room.exists() and not player.is_superuser:
            msg = 'Already in game'
            return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)
        room.members.add(request.user)
        return Response(data={'status': 'ok'}, status=status.HTTP_200_OK)


class LogoutFromRoomView(GenericAPIView):
    @property
    def allowed_methods(self):
        return ['get']

    def get(self, request, pk, format=None):
        response = Response()
        room = Room.objects.get(pk=pk)
        room.members.remove(request.user)
        player = Player.objects.get(id=request.user.id)
        if player.administration_room.exists():
            player.administration_room.remove(room)
            room.delete()
        return response

