import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from account.models import Customer

# 제품
class Product(models.Model):
    class Meta:
        verbose_name = "제품"

    name = models.CharField(max_length=30, verbose_name="상품 이름")
    manufacturer = models.CharField(max_length=30, verbose_name="제조사")
    description = models.TextField(verbose_name="상품 설명")
    registerDate = models.DateTimeField(auto_now_add=True, verbose_name="등록일")
    category = models.ForeignKey('ProductCategory', null=False, blank=False, on_delete=models.CASCADE, related_name="productCategory", verbose_name="소속 카테고리")
    likers = models.ManyToManyField(Customer, blank=True, related_name='productLikers', verbose_name="좋아요")
    likeCount = models.PositiveIntegerField(default=0, verbose_name='좋아요 수')
    productImage = models.ImageField(upload_to="product_image/", null=False, verbose_name="상품 이미지")

    def __str__(self):
        return f"{self.manufacturer}) {self.name}"

    def averageScore(self):
        reviews = PenReview.objects.filter(product=self)
        if len(reviews) == 0:
            return 0
        else:
            return sum(list(map(lambda r: r.totalScore, reviews))) / len(reviews)

    def getShortDescription(self):
        return self.description if len(self.description) < 20 else self.description[:17] + "..."


# 제품 관련 영상 링크
class ProductVideoLink(models.Model):
    class Meta:
        verbose_name = "상품 관련 유튜브 영상 링크"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, related_name='linkTargetProduct', verbose_name="대상 상품")
    videoLink = models.CharField(max_length=100, verbose_name="유튜브 링크")

# 제품 카테고리
class ProductCategory(models.Model):
    class Meta:
        verbose_name = "제품 카테고리"

    categoryName = models.CharField(max_length=15, verbose_name="카테고리 이름")

    def __str__(self):
        return f"{self.id}. {self.categoryName}"

# 웹 판매 정보
class WebSellInfo(models.Model):
    class Meta:
        verbose_name = "웹 판매 정보"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, related_name='webSellInfoTargetProduct', verbose_name="대상 상품")
    seller = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='webSellInfoSeller', verbose_name="웹 판매자")
    link = models.CharField(max_length=300, null=False, blank=False, verbose_name="판매정보 링크")
    price = models.PositiveIntegerField(null=False, blank=False, verbose_name="판매가")
    reported = models.BooleanField(default=False, verbose_name="신고")

    def __str__(self):
        reported = "🚨" if self.reported else ""
        return f"{reported} 판매자 : {self.seller.nickname}"

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
    class Meta:
        verbose_name = "제품 리뷰"

    author = models.ForeignKey("account.Customer", on_delete=models.CASCADE, null=True, related_name='reviewAuthor', verbose_name="리뷰 작성자")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='reviewTargetProduct', verbose_name="대상 상품")
    pub_date = models.DateTimeField(null=True, blank=True, verbose_name="리뷰 작성일")
    totalScore = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=False, verbose_name="총점")
    comment = models.CharField(max_length=50, default="", null=False, blank=False, verbose_name="한줄평")
    goodPoint = models.TextField(verbose_name="장점")
    weakPoint = models.TextField(verbose_name="단점")
    likers = models.ManyToManyField(Customer, related_name='reviewLikers', verbose_name="좋아요")
    likeCount = models.PositiveIntegerField(default=0, verbose_name='좋아요 수')

    reported = models.BooleanField(default=False, verbose_name="신고")
    modified = models.BooleanField(default=False, verbose_name="수정")

    reviewImage1 = models.ImageField(upload_to="review_image/", blank=True, null=True, verbose_name="리뷰 이미지1")
    reviewImage2 = models.ImageField(upload_to="review_image/", blank=True, null=True, verbose_name="리뷰 이미지2")
    reviewImage3 = models.ImageField(upload_to="review_image/", blank=True, null=True, verbose_name="리뷰 이미지3")
    reviewImage4 = models.ImageField(upload_to="review_image/", blank=True, null=True, verbose_name="리뷰 이미지4")
    reviewImage5 = models.ImageField(upload_to="review_image/", blank=True, null=True, verbose_name="리뷰 이미지5")
    reviewImage6 = models.ImageField(upload_to="review_image/", blank=True, null=True, verbose_name="리뷰 이미지6")

    tags = models.ManyToManyField('ReviewTag', blank=True)
    rawTagString = models.TextField(null=False, blank=True, default="", verbose_name="제품 태그 목록 원본 데이터")

    def getRoundTotalScore(self):
        strScore = str(self.totalScore)
        tokens = strScore.split('.')
        return f"{tokens[0]}.{tokens[1][:1]}"

    def getShortComment(self):
        return self.comment if len(self.comment) < 20 else self.comment[:17] + "..."

    def getTooltip(self):
        user = self.author

        try:
            user_usage = ("주 사용 용도", user.usage, Customer.usage_dict[user.usage])
        except:
            user_usage = ("주 사용 용도", "U0", "기타")

        try:
            user_job = ("직업", user.job, Customer.job_dict[user.job])
        except:
            user_job = ("직업", "J0", "기타")

        try:
            user_age = ("연령", user.age, Customer.age_dict[user.age])
        except:
            user_age = ("연령", "etcs", "기타")

        userPropertyList = list(filter(lambda choice: choice[-1] != "기타", [user_usage, user_job, user_age]))

        if len(userPropertyList) <= 0 :
            return "모든 정보가 비공개 되어 있습니다."
        
        else :
            return " | ".join([f"{p[-1]}" for p in userPropertyList])

# 점수
class Score(models.Model):
    class Meta:
        verbose_name = "제품 별점"

    review = models.ForeignKey(Review, on_delete=models.CASCADE, blank=False, null=True, related_name="scoreTargetReview", verbose_name="대상 리뷰")
    name = models.CharField(max_length=20, verbose_name="평가 항목")
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=1, verbose_name="평가 점수")

    def __str__(self):
        return self.name + " : " + str(self.score) + "점"

# 펜 리뷰
class PenReview(Review):
    class Meta:
        verbose_name = "펜 리뷰"

    grip = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=True, related_name='grip', verbose_name="그립감")
    life = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=True, related_name='life', verbose_name="제품 수명")
    durability = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=True, related_name='durability', verbose_name="내구도")
    design = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=True, related_name='design', verbose_name="디자인")
    texture = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=True, related_name='texture', verbose_name="사용감")
    costEffetiveness = models.ForeignKey(Score, on_delete=models.CASCADE, blank=False, null=True, related_name='costEffetiveness', verbose_name="가성비")

    def __str__(self):
            description = self.comment if len(self.comment) <= 10 else (self.comment[:10] + "...")
            return f"{self.product.name}) {description}"

# 상품의 특성
class ReviewTag(models.Model):
    class Meta:
        verbose_name = "리뷰 태그"

    targetReview = models.ManyToManyField('Review', blank=True, verbose_name="가리키는 상품")
    tag = models.CharField(max_length=15, verbose_name="상품 태그")

    def __str__(self):
        return self.tag

class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="commentTargetReview", verbose_name="대상 리뷰")
    author = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='commentAuthor', verbose_name="리뷰 작성자")
    pub_date = models.DateTimeField(verbose_name="리뷰 작성(수정)일")
    body = models.TextField(verbose_name="댓글 내용")

    def __str__(self):
        return f"{self.body[:10]}.. (by {self.author.nickname}, on {self.pub_date}" 


# 상품 등록 요청
class ProductRequest(models.Model):
    class Meta:
        verbose_name = "상품 등록 요청"
    
    author = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="productRequestAuthor", verbose_name="제품 등록 요청자")
    productName = models.CharField(max_length=20, null=False, blank=False, verbose_name="제품 이름")
    productBrand = models.CharField(max_length=20, null=True, blank=True, verbose_name="제품 브랜드")
    productDescription = models.TextField(null=True, blank=True, verbose_name="제품 설명")
    isChecked = models.BooleanField(default=False, verbose_name="확인여부")

    def __str__(self):
        return self.productName

    def getShortDescription(self):
        return self.productDescription if len(self.productDescription) < 50 else self.productDescription[:57] + "..."