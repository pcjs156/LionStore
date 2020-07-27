from django.db import models
from django.contrib.auth.models import AbstractUser

# 기본 Custom User Model / 일반 리뷰어
class Customer(AbstractUser):
    is_Customer = models.BooleanField('customer status', default=False)
    is_WebSeller = models.BooleanField('webSeller status', default=False)
    is_Stationer = models.BooleanField('stationer status', default=False)

    # 닉네임(또는 상호명)
    nickname = models.CharField(max_length=15, blank=False, null=False, verbose_name="닉네임/상호명")
    
    # 사용자 대표 이미지
    # 빈 값으로 form에 입력될 경우 기본 이미지로 대체되어야 함
    image = models.ImageField(upload_to="user_profile_image/", blank=True, null=False, verbose_name="대표 이미지")

    # 소개글
    introduce = models.TextField(verbose_name="소개글")

    def __str__(self):
        return "[C] " + self.username

    

# 판매자(웹/문방구) 공통
class Seller(Customer):
    # 연락처
    telephone = models.CharField(max_length=20, blank=False, null=False, default="", verbose_name="판매자 연락처")


# 웹 쇼핑몰 판매자
class WebSeller(Seller):
    # 웹페이지 메인 주소
    link = models.CharField(max_length=200, blank=False, null=False, default="", verbose_name="웹 쇼핑몰 메인 주소")

    def __str__(self):
        return "[W] " + self.username

# 문방구 사장님
class Stationer(Seller):
    # 문방구 위치 위도
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name="문방구 위치 위도")
    # 문방구 위치 경도
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name="문방구 위치 경도")

    def __str__(self):
        return "[S] " + self.username