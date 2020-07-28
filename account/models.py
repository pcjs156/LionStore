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
    image = models.ImageField(upload_to="user_profile_image/", blank=True, null=False, verbose_name="대표 이미지")

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


    # 유저 특성(고정)
    AGE = (
        ("10s", "10"),
        ("20s", "20"),
        ("30s", "30"),
        ("40s", "40"),
        ("50s", "50"),
        ("60s", "60"),
        ("etcs", "기타")
    )
    age = models.CharField(max_length=5, default=("etcs", "기타"), blank=False, null=False, choices=AGE, verbose_name="연령대")

    JOB = (
        ("J1", "학생"),
        ("J2", "직장인"),
        ("J3", "사업가"),
        ("J4", "기타"),
    )
    job = models.CharField(max_length=10, default=("J4", "기타"), blank=False, null=False, choices=JOB, verbose_name="직업")


    USAGE = (
        ("U1", "그림그리기"),
        ("U2", "문서작성"),
        ("U3", "다이어리 꾸미기"),
        ("U4", "필기(공부 혹은 시험)"),
        ("U5", "기타"),
    )
    usage = models.CharField(max_length=20, default=("U5", "기타"), blank=False, null=False, choices=USAGE, verbose_name="주 사용 용도")

    # 이 경우 펜을 복수선택할 수 있게 하려면..
    # 1. 가입 이후 ManyToManyField를 이용해 따로 설정한다.
    # 2. 최대 관심 펜 종류를 정해놓고 고정 ForeignKey? 를 설정한다.
    #    -> 이때 기본값을 '기타'로 놓는 방법으로 값이 채워지지 않는 경우가 없도록 한다.
    #       (홈페이지에서 유저의 리뷰를 볼 때 '기타'는 표시되지 않도록 한다.)
    
    # 방법 2로 구현한다. 이때 기본 값은 "기타", 최대 관심 펜 갯수는 3개.
    PEN = (
        ("P1", "형광펜"),
        ("P2", "유성펜"),
        ("P3", "볼펜"),
        ("P4", "샤프펜슬"),
        ("P5", "기타"),
    )
    penInterest_1 = models.CharField(max_length=10, blank=False, null=False, choices=PEN, default=("P5", "기타"), verbose_name="관심 펜 1순위")
    penInterest_2 = models.CharField(max_length=10, blank=False, null=False, choices=PEN, default=("P5", "기타"), verbose_name="관심 펜 2순위")
    penInterest_3 = models.CharField(max_length=10, blank=False, null=False, choices=PEN, default=("P5", "기타"), verbose_name="관심 펜 3순위")
    

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