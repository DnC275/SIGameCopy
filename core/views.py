import jwt
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.conf import settings
from django.core import serializers as django_serializers
# from django.contrib.auth import get_user_model, authenticate

from .models import *
from .serializers import *


class PlayerViewSet(ModelViewSet):
    queryset = Player.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return PlayerShortSerializer
        return PlayerSerializer


class SignUpViewSet(CreateAPIView):
    model = Player
    permission_classes = [AllowAny,]
    serializer_class = PlayerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response = Response(data={'status': 'created'}, status=status.HTTP_201_CREATED)
        return response


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AuthByEmailPasswordSerializer

    @property
    def allowed_methods(self):
        return ['post']

    def get_serializer_context(self):
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request):
        if not request.data and isinstance(request.user, Player):
            return Response(data={'email': request.user.email, 'username': request.user.username}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.data

        token = jwt.encode({
            'id': data['id']
        }, settings.SECRET_KEY, algorithm='HS256')

        data.pop('id')

        response = Response(data=data, status=status.HTTP_200_OK)
        response.set_cookie('access_token', token, secure=True)
        response.cookies['access_token']['samesite'] = None
        response['Access-Control-Allow-Origin'] = 'Authorization'

        return response


class LogoutView(APIView):
    @property
    def allowed_methods(self):
        return ['get']

    def get(self, request, format=None):
        # request.auth.delete()

        response = Response()
        response.delete_cookie('access_token')
        return response


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
        if admin.administration_room.exists() and not admin.is_superuser:
            msg = 'Already in game'
            return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(admin=admin)
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
        room.has_access.add(request.user)

        return Response(data={'status': 'ok'}, status=status.HTTP_200_OK)
