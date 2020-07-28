import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from django.db import models

from account.models import Customer

# 제품
class Product(models.Model):
    class Meta:
        verbose_name = "제품"

    name = models.CharField(max_length=30, verbose_name="상품 이름")
    manufacturer = models.CharField(max_length=30, verbose_name="제조사")
    description = models.TextField(verbose_name="제조사")
    likers = models.ManyToManyField(Customer, related_name='productLikers', verbose_name="좋아요")

# 제품 이미지
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, related_name='imageTargetProduct', verbose_name="대상 상품")
    productImage = models.ImageField(upload_to="product_image/", null=False, verbose_name="상품 이미지")

# 제품 관련 영상 링크
class ProductVideoLink(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, related_name='linkTargetProduct', verbose_name="대상 상품")
    videoLink = models.CharField(max_length=100, verbose_name="유튜브 링크")

# 웹 판매 정보
class WebSellInfo(models.Model):
    class Meta:
        verbose_name = "웹 판매 정보"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, related_name='webSellInfoTargetProduct', verbose_name="대상 상품")
    seller = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='webSellInfoSeller', verbose_name="웹 판매자")
    link = models.CharField(max_length=300, verbose_name="판매정보 링크")
    price = models.PositiveIntegerField(verbose_name="판매가")
    reported = models.BooleanField(default=False, verbose_name="신고")

# 문방구 판매 정보
class StationerSellInfo(models.Model):
    class Meta:
        verbose_name = "문방구 판매 정보"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, related_name='StationerSellInfoTargetProduct', verbose_name="대상 상품")
    seller = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='StationerSellInfoSeller', verbose_name="문방구 판매자")
    price = models.PositiveIntegerField(verbose_name="판매가")
    reported = models.BooleanField(default=False, verbose_name="신고")

# 리뷰
class Review(models.Model):
    author = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='reviewAuthor', verbose_name="리뷰 작성자")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, related_name='reviewTargetProduct', verbose_name="대상 상품")
    totalScore = models.ForeignKey('Score', on_delete=models.CASCADE, null=False, blank=False, related_name="reviewTotalScore", verbose_name="총점")
    goodPoint = models.TextField(verbose_name="장점")
    weakPoint = models.TextField(verbose_name="단점")
    likers = models.ManyToManyField(Customer, related_name='reviewLikers', verbose_name="좋아요")
    reported = models.BooleanField(default=False, verbose_name="신고")

# 0~5까지 값이 주어질 수 있도록 재정의된 IntegerField
class RangedScoreField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)

# 점수
class Score(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, blank=False, null=False, related_name="scoreTargetReview", verbose_name="대상 리뷰")
    name = models.CharField(max_length=20, verbose_name="평가 항목")
    score = RangedScoreField(min_value=0, max_value=5, verbose_name="평가 점수")

# 펜 리뷰
class PenReview(models.Model):
    class Meta:
        verbose_name = "펜 리뷰"

    grip = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=False, related_name='grip', verbose_name="그립감")
    life = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=False, related_name='life', verbose_name="제품 수명")
    durability = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=False, related_name='durability', verbose_name="내구도")
    design = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=False, related_name='design', verbose_name="디자인")
    texture = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=False, related_name='texture', verbose_name="사용감")
    costEffetiveness = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=False, related_name='costEffetiveness', verbose_name="가성비")
    versatility = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=False, related_name='versatility', verbose_name="범용성")

# 상품의 특성
class ProductTag(models.Model):
    class Meta:
        verbose_name = "상품 태그"

    review = models.ForeignKey(Review, on_delete=models.CASCADE, blank=False, null=False, related_name="tagTargetReview", verbose_name="대상 리뷰")
    tag = models.CharField(max_length=15, verbose_name="상품 태그")

# 리뷰 이미지
class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=False, related_name='reviewImageTargetReview', verbose_name="대상 리뷰")
    reviewImage = models.ImageField(upload_to="review_image/", blank=True, null=True, verbose_name="리뷰 이미지")
