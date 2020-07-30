from django.db import models
from django.contrib.auth.models import AbstractUser

# 기본 Custom User Model / 일반 리뷰어
class Customer(AbstractUser):
    class Meta:
        verbose_name = "유저"

    is_Customer = models.BooleanField('customer status', default=False)
    is_WebSeller = models.BooleanField('webSeller status', default=False)
    is_Stationer = models.BooleanField('stationer status', default=False)

    # 닉네임(또는 상호명)
    nickname = models.CharField(max_length=15, blank=False, null=False, verbose_name="닉네임/상호명")
    
    # 사용자 대표 이미지
    # 빈 값으로 form에 입력될 경우 기본 이미지로 대체되어야 함
    image = models.ImageField(upload_to="account/profile_image", default="account/profile_image/user_default_image.png", blank=True, null=True, verbose_name="대표 이미지")

    # 소개글
    introduce = models.TextField(verbose_name="소개글")

    # 연락처
    telephone = models.CharField(max_length=20, blank=False, null=False, default="", verbose_name="판매자 연락처")

    # 웹페이지 메인 주소
    link = models.CharField(max_length=200, blank=False, null=False, default="", verbose_name="웹 쇼핑몰 메인 주소")

    # 문방구 위치 위도
    latitude = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name="문방구 위치 위도")
    # 문방구 위치 경도
    longitude = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name="문방구 위치 경도")


    AGE = (
        ("etcs", "기타"),
        ("10s", "10대"),
        ("20s", "20대"),
        ("30s", "30대"),
    )
    age = models.CharField(max_length=5, default=("etcs", "기타"), blank=False, null=False, choices=AGE, verbose_name="연령대")

    JOB = (
        ("J0", "기타"),
        ("J1", "학생"),
        ("J2", "아티스트"),
    )
    job = models.CharField(max_length=10, default=("J0", "기타"), blank=False, null=False, choices=JOB, verbose_name="직업")


    USAGE = (
        ("U0", "기타"),
        ("U1", "공부/필기"),
        ("U2", "문서 작성"),
        ("U3", "드로잉"),
        ("U4", "다이어리 꾸미기"),
        ("U5", "캘리그라피"),
    )
    usage = models.CharField(max_length=20, default=("U0", "기타"), blank=False, null=False, choices=USAGE, verbose_name="주 사용 용도")

    PEN = (
        ("P0", "기타"),
        ("P1", "볼펜"),
        ("P2", "연필"),
        ("P3", "색연필"),
        ("P4", "만년필"),
        ("P5", "샤프펜슬"),
        ("P6", "형광펜"),
        ("P7", "유성펜"),
        ("P8", "젤펜"),
    )
    penInterest_1 = models.CharField(max_length=10, blank=False, null=False, choices=PEN, default=("P0", "기타"), verbose_name="관심 펜 1순위")
    penInterest_2 = models.CharField(max_length=10, blank=False, null=False, choices=PEN, default=("P0", "기타"), verbose_name="관심 펜 2순위")
    penInterest_3 = models.CharField(max_length=10, blank=False, null=False, choices=PEN, default=("P0", "기타"), verbose_name="관심 펜 3순위")
    

    # 유저 태그(추가)
    tags = models.ManyToManyField('account.CustomerTag', blank=True, verbose_name="유저 설명 태그")

    def __str__(self):
        if self.is_Customer:
            typeMarker = "[C]"
        elif self.is_WebSeller:
            typeMarker = "[W]"
        elif self.is_Stationer:
            typeMarker = "[S]"
        else:
            typeMarker = "[UNKNOWN]"
        
        return f"{typeMarker} {self.username}"



class CustomerTag(models.Model):
    class Meta:
        verbose_name = "유저 태그"

    targetCustomer = models.ManyToManyField(Customer)
    tagBody = models.CharField(max_length=10)