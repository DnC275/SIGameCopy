from django.apps import AppConfig


class RoomsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.rooms'


    def ready(self):
        import core.rooms.receivers
