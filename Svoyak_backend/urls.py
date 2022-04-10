"""Svoyak_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core.players.views import *
from core.rooms.views import *
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import path, include
# from rest_framework.authtoken.views import obtain_auth_token


router = routers.DefaultRouter()

router.register(r'rooms', RoomViewSet, basename='rooms')
router.register(r'players', PlayerViewSet, basename='players')
schema_view = get_schema_view(
   openapi.Info(
      title="Svoyak backend",
      default_version='v1',
      description="Бэкэнд для Svoyak"
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/signup/', SignUpViewSet.as_view(), name='sign_up'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/rooms/<int:pk>/login/', LoginToRoomView.as_view(), name='login_to_room'),
    path('api/rooms/<int:pk>/logout/', LogoutFromRoomView.as_view(), name='logout_from_room'),
    # path('api/players/', PlayerViewSet.as_view({'get': 'list'}), name='players'),
    path('api/', include(router.urls)),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]
