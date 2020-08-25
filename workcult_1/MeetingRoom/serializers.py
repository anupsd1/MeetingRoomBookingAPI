from rest_framework import serializers, mixins
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import MeetingRoom, MonthlyUsage
from LocalUser.models import Company, UserProfile, LocalUser
from . import makeinvoice2
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from knox.auth import TokenAuthentication

from itertools import chain
from operator import attrgetter


class MeetingRoomSerializer(serializers.HyperlinkedModelSerializer):
    allowed = serializers.ReadOnlyField()
    # file = makeinvoice2.render_pdf_view()
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    class Meta:
        model = MeetingRoom
        fields = ('id', 'company', 'start', 'end', 'allowed')
