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
                  'nickname', 'introduce', 'image',
                  'age', 'job', 'usage',
                  'penInterest_1', 'penInterest_2', 'penInterest_3', 'rawTagString']
    
    @transaction.atomic
    def save(self):
        user = super().save()
        user.is_Customer = True
        user.save()
        return user


class WebSellerSignUpForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['username', 'password1', 'password2', 'email',
                  'nickname', 'introduce', 'image',
                  'telephone', 'link']
    
    @transaction.atomic
    def save(self):
        user = super().save()
        user.is_WebSeller = True
        user.save()
        return user


class StationerSignUpForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['username', 'password1', 'password2', 'email',
                  'nickname', 'introduce', 'image',
                  'telephone', 'latitude', 'longitude']
    
    @transaction.atomic
    def save(self):
        user = super().save()
        user.is_Stationer = True
        user.save()
        return user