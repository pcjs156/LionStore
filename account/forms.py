from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction

from account.models import Customer

user = get_user_model()

class UserLoginForm(AuthenticationForm):
    class Meta:
        fields = ['username', 'password']

class UserSignUpForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['username', 'password1', 'password2', 'email',
                  'nickname', 'introduce', 'image']
    
    @transaction.atomic
    def save(self):
        user = super().save()
        user.is_Customer = True
        user.save()
        return user