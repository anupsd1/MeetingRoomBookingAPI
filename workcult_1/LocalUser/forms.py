from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import LocalUser
from django import forms
from django.contrib.auth import get_user_model

#User = get_user_model()

# Create your views here.
# class CustomUserCreationForm(UserCreationForm):
#     class Meta(UserCreationForm):
#         model = LocalUser
#         fields = '__all__'


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = LocalUser
        fields = '__all__'

