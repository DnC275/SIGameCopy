from django.contrib import admin
from .models import *


class PlayerAdmin(admin.ModelAdmin):
    fields = ('email', 'username', 'password')


admin.site.register(Player, PlayerAdmin)
admin.site.register(Room)
