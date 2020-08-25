from django.contrib import admin
from django.urls import path

from . import views

# /account/...
urlpatterns = [
    # 마이 페이지
    path('myPage/', views.myPage_view, name='myPage'),
    path('myPageRedirector/<target>', views.myPageRedirector, name="myPageRedirector"),

    # 로그인 / 로그아웃 / 회원가입 관련
    path('logIn/', views.login_view, name='logIn'),
    path('logOut/', views.logout_view, name='logOut'),
    path('signUp/', views.selectCustomerType_view, name='selectCustomerType'),
    path('signUp/sellerType/', views.selectSellerType_view, name='selectSellerType'),
    path('signUp/user/', views.userSignUp_view, name='userSignUp'),
    path('signUp/webSeller/', views.webSellerSignUp_view, name='webSellerSignUp'),
    path('signUp/stationer/', views.stationerSignUp_view, name='stationerSignUp'),
    path('setLocation/', views.setLocation_view, name="setLocation"),

    # 계정 정보 수정 관련
    path('modifyUserInfo/', views.modifyUserInfo_view, name='modifyUserInfo'),

    # 작성한 웹 판매 정보 목록
    path('webSellInfoList/', views.webSellerInfoList_view, name='webSellInfoList'),
    # 작성한 문구점 판매 정보 목록
    path('stationerSellInfoList/', views.stationerSellInfoList_view, name='stationerSellInfoList'),
]
