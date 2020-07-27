from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('logIn/', views.login_view, name='logIn'),
    path('logOut/', views.logout_view, name='logOut'),
    path('signUp/', views.selectCustomerType_view, name='selectCustomerType'),
    path('signUp/user/', views.userSignUp_view, name='userSignUp'),
    path('signUp/webSeller/', views.webSellerSignUp_view, name='webSellerSignUp'),
    path('signUp/stationer/', views.stationerSignUp_view, name='stationerSignUp'),
]
