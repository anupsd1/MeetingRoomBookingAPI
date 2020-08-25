from django.contrib import admin
from .models import MeetingRoom, MonthlyUsage, Invoice


# Register your models here.
admin.site.register(MeetingRoom)
# admin.site.register(Invoice)
admin.site.register(MonthlyUsage)
admin.site.register(Invoice)
