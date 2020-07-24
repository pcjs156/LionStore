from django.db import models
from django.contrib.auth.models import AbstractUser

# 기본 Custom User Model / 일반 리뷰어
class Customer(AbstractUser):
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customer"

    PASSWORD_QUESTION = (
        ("q1", "기억에 남는 추억의 장소는?"),
        ("q2", "자신의 인생 좌우명은?"),
        ("q3", "부모님의 결혼 기념일은?"),
        ("q4", "출신 초등학교는?"),
        ("q5", "소주 맥주 막걸리 중 가장 좋아하는 술은?"),
    )
    
    # 닉네임(또는 상호명)
    nickname = models.CharField(max_length=15, blank=False, null=False, verbose_name="닉네임/상호명")

    # 비밀번호 찾기 질문 / 답
    password_question = models.CharField(max_length=30, blank=False, null=False, choices=PASSWORD_QUESTION, verbose_name="비밀번호 찾기 질문")
    password_answer = models.CharField(max_length=30, blank=False, null=False, verbose_name="비밀번호 찾기 답")
    
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
    telephone = models.CharField(max_length=20, blank=False, null=False, verbose_name="판매자 연락처")


# 웹 쇼핑몰 판매자
class WebSeller(Seller):
    class Meta:
        verbose_name = "WebSeller"
        verbose_name_plural = "WebSeller"

    # 웹페이지 메인 주소
    link = models.CharField(max_length=200, blank=False, null=False, verbose_name="웹 쇼핑몰 메인 주소")

    def __str__(self):
        return "[W] " + self.username

# 문방구 사장님
class Stationer(Seller):
    class Meta:
        verbose_name = "Stationer"
        verbose_name_plural = "Stationer"

    # 문방구 위치 위도
    latitude = models.DecimalField(max_digits=10, decimal_places=6, verbose_name="문방구 위치 위도")
    # 문방구 위치 경도
    longitude = models.DecimalField(max_digits=10, decimal_places=6, verbose_name="문방구 위치 경도")

    def __str__(self):
        return "[S] " + self.username