from django.contrib import admin
from .models import Player


class PlayerAdmin(admin.ModelAdmin):
    fields = ('email', 'username', 'password')


admin.site.register(Player, PlayerAdmin)

