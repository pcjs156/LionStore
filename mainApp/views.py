from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.db.models.fields.files import ImageFieldFile

from .models import *

from .forms import PenReviewForm

from .tools import *


def intro_view(request):
    return render(request, 'intro.html')


def mainPage_view(request):
    content = dict()

    # 테스트/개발용이므로 서비스 할 때는 빠져아 함
    # 카테고리가 존재하지 않는 경우에만 하단의 모든 카테고리를 새로 생성하는 역할
    initializeCategory()
    # 랜덤으로 countLimit개까지 Product를 생성하고 임의로 카테고리를 지정
    automativeFilling_Product(countLimit=50)

    볼펜 = ProductCategory.objects.get(categoryName="볼펜")
    만년필 = ProductCategory.objects.get(categoryName="만년필")
    캘리그라피펜 = ProductCategory.objects.get(categoryName="캘리그라피펜")
    연필 = ProductCategory.objects.get(categoryName="연필")
    색연필 = ProductCategory.objects.get(categoryName="색연필")
    형광펜 = ProductCategory.objects.get(categoryName="형광펜")
    샤프펜슬 = ProductCategory.objects.get(categoryName="샤프펜슬")
    유성펜 = ProductCategory.objects.get(categoryName="유성펜")
    사인펜 = ProductCategory.objects.get(categoryName="사인펜")
    젤펜 = ProductCategory.objects.get(categoryName="젤펜")
    기타 = ProductCategory.objects.get(categoryName="기타")

    categoryDict = {'볼펜': 볼펜, '만년필': 만년필, '캘리그라피펜': 캘리그라피펜, '연필': 연필, '색연필': 색연필,
                    '형광펜': 형광펜, '샤프펜슬': 샤프펜슬, '유성펜': 유성펜, '사인펜': 사인펜, '젤펜': 젤펜, '기타': 기타}
    content.update(categoryDict)

    newReviews = PenReview.objects.all().order_by('-pub_date')[:10]
    content['newReviews'] = newReviews

    popularReviews = PenReview.objects.all().order_by('likeCount')[:10]
    content['popularReviews'] = popularReviews
    

    return render(request, 'mainPage.html', content)


@login_required(login_url='/account/logIn/')
def newProductRequest_view(request):
    return render(request, 'newProductRequest.html')


def productList_view(request, category_id):
    content = dict()

    currentCategory = ProductCategory.objects.get(pk=category_id)
    content['products'] = Product.objects.filter(category=currentCategory)

    return render(request, 'productList.html', content)


def productDetail_view(request, product_id):
    content = dict()

    # 대상 제품 정보
    product = Product.objects.get(pk=product_id)
    content['product'] = product

    # 좋아요 관련
    likers = [str(customer.nickname) for customer in product.likers.all()]
    if len(likers) == 0:
        likeMessage = "아직 좋아요가 눌리지 않았습니다."
    elif len(likers) == 1:
        likeMessage = f"{likers[0]}님이 이 제품을 좋아합니다."
    else:
        likeMessage = f"{likers[0]}님 외 {len(likers)-1}명이 이 제품을 좋아합니다."
    content['likeMessage'] = likeMessage
    content['userLike'] = product.likers.filter(username=request.user.username).exists()

    # 비디오 링크 관련
    videoLinks = ProductVideoLink.objects.filter(product=product)
    videoLinkHashs = [getHash(linkObj.videoLink)for linkObj in videoLinks]
    content['videoLinkHashs'] = videoLinkHashs

    # 리뷰 관련
    reviews = PenReview.objects.filter(product=product).order_by('pub_date')
    content['reviews'] = reviews

    return render(request, 'productDetail.html', content)


# 좋아요 버튼을 눌렀을 때 좋아요가 눌려 있지 않았다면 좋아요 처리, 좋아요가 눌려 있었다면 좋아요 해제
@login_required(login_url='/account/logIn')
def productLikeProcess(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    category_id = product.category.id

    if not product.likers.filter(username=request.user.username).exists():
        productLike(request, product_id, category_id)
    else:
        productDislike(request, product_id, category_id)

    return redirect(f"/store/productDetail/{product_id}")


@login_required(login_url='/account/logIn/')
def productLike(request, product_id, category_id):
    product : Product = get_object_or_404(Product, pk=product_id)
    product.likers.add(request.user)
    product.likeCount += 1
    product.save()


@login_required(login_url='/account/logIn/')
def productDislike(request, product_id, category_id):
    product = get_object_or_404(Product, pk=product_id)
    product.likers.remove(request.user)
    product.likeCount -= 1
    product.save()


def productRequest_view(request):
    return render(request, 'productRequest.html')


def productRequestDetail_view(request, product_request_id):
    return render(request, 'productRequestDetail.html')


@login_required(login_url='/account/logIn/')
def newProductRequestDetail_view(request, product_request_id):
    return render(request, 'newProductRequestDetail.html')


@login_required(login_url='/account/logIn/')
def productRequestModify_view(request, product_request_id):
    return render(request, 'productRequestModify.html')


def rateBackUp_view(request):
    return render(request, 'rateBackUp.html')


@login_required(login_url='/account/logIn/')
def reviewCreate_view(request, product_id):
    if request.method == 'POST':
        form = PenReviewForm(request.POST, request.FILES)

        product = Product.objects.get(pk=product_id)
        new_review : PenReview = form.save()
        new_review.product = product
        new_review.author = request.user
        new_review.pub_date = timezone.now()
        new_review.goodPoint = request.POST['goodPoint']
        new_review.weakPoint = request.POST['weakPoint']
        new_review.save()

        new_review.totalScore = Score.objects.create(
            review=new_review, name="총점", score=int(request.POST['totalScore']))
        new_review.grip = Score.objects.create(
            review=new_review, name="그립감", score=int(request.POST['grip']))
        new_review.life = Score.objects.create(
            review=new_review, name="제품 수명", score=int(request.POST['life']))
        new_review.durability = Score.objects.create(
            review=new_review, name="내구도", score=int(request.POST['durability']))
        new_review.design = Score.objects.create(
            review=new_review, name="디자인", score=int(request.POST['design']))
        new_review.texture = Score.objects.create(
            review=new_review, name="사용감", score=int(request.POST['texture']))
        new_review.costEffetiveness = Score.objects.create(
            review=new_review, name="가성비", score=int(request.POST['costEffetiveness']))
        new_review.versatility = Score.objects.create(
            review=new_review, name="범용성", score=int(request.POST['versatility']))
        new_review.save()

        # 리뷰 이미지를 하나도 올리지 않았다면 대상 제품의 대표 이미지로 변경
        if not hasImageField(new_review):
            new_review.reviewImage1 = product.productImage
            new_review.save()

        return productDetail_view(request, product_id)

    else:
        form = PenReviewForm()
        return render(request, 'reviewCreate.html', {'form': form})


def reviewDetail_view(request, review_id):
    content = dict()

    review = PenReview.objects.get(pk=review_id)
    content['review'] = review

    # 작성자
    content['author'] = review.author.nickname
    # 제품명
    content['product'] = review.product.name
    # 장점
    content['goodPoint'] = review.goodPoint
    # 단점
    content['weakPoint'] = review.weakPoint
    
    # 제품 총점
    content['totalScore'] = review.totalScore
    # 그립감
    content['gripScore'] = review.grip
    # 수명
    content['lifeScore'] = review.life
    # 내구도
    content['durabilityScore'] = review.durability
    # 디자인
    content['designScore'] = review.design
    # 사용감
    content['textureScore'] = review.texture
    # 가성비
    content['costEffetivenessScore'] = review.costEffetiveness
    # 범용성
    content['versatilityScore'] = review.versatility

    # 좋아요 관련
    likers = [str(customer.nickname) for customer in review.likers.all()]

    if len(likers) == 0:
        likeMessage = "아직 좋아요가 눌리지 않았습니다."
    elif len(likers) == 1:
        likeMessage = f"{likers[0]}님이 이 리뷰를 좋아합니다."
    else:
        likeMessage = f"{likers[0]}님 외 {len(likers)-1}명이 이 리뷰를 좋아합니다."
    content['likeMessage'] = likeMessage
    content['userLike'] = review.likers.filter(username=request.user.username).exists()

    # 현재 사용자가 해당 리뷰의 작성자인가?
    isAuthor = (request.user == review.author)
    content['isAuthor'] = isAuthor

    return render(request, 'reviewDetail.html', content)

# 좋아요 버튼을 눌렀을 때 좋아요가 눌려 있지 않았다면 좋아요 처리, 좋아요가 눌려 있었다면 좋아요 해제
@login_required(login_url='/account/logIn')
def reviewLikeProcess(request, review_id):
    review = get_object_or_404(PenReview, pk=review_id)

    if not review.likers.filter(username=request.user.username).exists():
        reviewLike(request, review_id)
    else:
        reviewDislike(request, review_id)

    return redirect(f"/store/reviewDetail/{review_id}")


@login_required(login_url='/account/logIn/')
def reviewLike(request, review_id):
    review = get_object_or_404(PenReview, pk=review_id)
    review.likers.add(request.user)
    review.likeCount += 1
    review.save()


@login_required(login_url='/account/logIn/')
def reviewDislike(request, review_id):
    review = get_object_or_404(PenReview, pk=review_id)
    review.likers.remove(request.user)
    review.likeCount -= 1
    review.save()

@login_required(login_url='/account/logIn/')
def reviewModify_view(request, review_id):
    content = dict()

    review = get_object_or_404(PenReview, pk=review_id)
    content['review'] = review

    return render(request, 'reviewModify.html', content)

@login_required(login_url='/account/logIn/')
def reviewUpdate(request, review_id):
    review : PenReview = get_object_or_404(PenReview, pk=review_id)

    review.pub_date = timezone.datetime.now()
    review.goodPoint = request.POST['goodPoint']
    review.weakPoint = request.POST['weakPoint']

    review.totalScore.score = request.POST['totalScore']
    review.totalScore.save()

    review.grip.score = request.POST['grip']
    review.grip.save()

    review.life.score = request.POST['life']
    review.life.save()

    review.durability.score = request.POST['durability']
    review.durability.save()

    review.design.score = request.POST['design']
    review.design.save()

    review.texture.score = request.POST['texture']
    review.texture.save()

    review.costEffetiveness.score = request.POST['costEffetiveness']
    review.costEffetiveness.save()

    review.versatility.score = request.POST['versatility']
    review.versatility.save()

    review.modified = True

    review.save()


    return redirect('/store/reviewDetail/' + str(review.id))



def searchMain_view(request):
    return render(request, 'searchMain.html')


def searchResult_view(request):
    return render(request, 'searchResult.html')


@login_required(login_url='/account/logIn/')
def stationerSellInfoCreate_view(request, category_id, product_id):
    return render(request, 'stationerSellInfoCreate.html')


def stationerSellInfoDetail_view(request, category_id, product_id, stationerSellInfo_id):
    return render(request, 'stationerSellInfoDetail.html')


@login_required(login_url='/account/logIn/')
def stationerSellInfoModify_view(request, category_id, product_id, stationerSellInfo_id):
    return render(request, 'stationerSellInfoModify.html')


@login_required(login_url='/account/logIn/')
def webSellInfoCreate_view(request, category_id, product_id):
    return render(request, 'webSellInfoCreate.html')


def webSellInfoDetail_view(request, category_id, product_id, webSellInfo_id):
    return render(request, 'webSellInfoDetail.html')


@login_required(login_url='/account/logIn/')
def webSellInfoModify_view(request, category_id, product_id, webSellInfo_id):
    return render(request, 'webSellInfoModify.html')


# 이하 테스트용(삭제 예정) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def categoryListTest_view(request):
    categoryList = ProductCategory.objects.all()

    return render(request, 'categoryListTest.html', {'categoryList': categoryList})

# def productListTest_view(request, category_id):
#     category = ProductCategory.objects.get(pk=category_id)
#     products = Product.objects.filter(category=category)

#     return render(request, 'productListTest.html', {'products':products})


def newReviewTest_view(request, product_id):
    if request.method == 'POST':
        form = PenReviewForm(request.POST)

        product = Product.objects.get(pk=product_id)
        new_review = PenReview(product=product)
        new_review.author = request.user
        new_review.pub_date = timezone.now()
        new_review.goodPoint = request.POST['goodPoint']
        new_review.weakPoint = request.POST['weakPoint']
        new_review.save()

        new_review.totalScore = Score.objects.create(
            review=new_review, name="총점", score=int(request.POST['totalScore']))
        new_review.grip = Score.objects.create(
            review=new_review, name="그립감", score=int(request.POST['grip']))
        new_review.life = Score.objects.create(
            review=new_review, name="제품 수명", score=int(request.POST['life']))
        new_review.durability = Score.objects.create(
            review=new_review, name="내구도", score=int(request.POST['durability']))
        new_review.design = Score.objects.create(
            review=new_review, name="디자인", score=int(request.POST['design']))
        new_review.texture = Score.objects.create(
            review=new_review, name="사용감", score=int(request.POST['texture']))
        new_review.costEffetiveness = Score.objects.create(
            review=new_review, name="가성비", score=int(request.POST['costEffetiveness']))
        new_review.versatility = Score.objects.create(
            review=new_review, name="범용성", score=int(request.POST['versatility']))

        new_review.save()
        return redirect('mainPage')

    else:
        form = PenReviewForm()
        return render(request, 'newReviewTest.html', {'form': form})


def newMapTest_view(request):
    if request.method == "POST":
        print(type(request.POST["stationerStoreLocation"]))

    return render(request, 'mapTest.html')


def newMapResult_view(request):
    return render(request, 'mapTestResult.html')
