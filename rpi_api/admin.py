from django.contrib import admin
from .models import RegisteredSensor, Image, Temperature, Logs, Power, IRSend

admin.site.register(RegisteredSensor)
admin.site.register(Temperature)
admin.site.register(Image)
admin.site.register(Logs)
admin.site.register(Power)
admin.site.register(IRSend)

admin.site.site_header = 'Raspberry Pi Dashboard'
