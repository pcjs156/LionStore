from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from .models import *
from account.models import CustomerTag

from .forms import PenReviewForm
from .forms import NewProductRequestForm

from .tools import *


def intro_view(request):
    return render(request, 'intro.html')


def productList_view(request, category_id):
    content = dict()

    category = ProductCategory.objects.get(pk=category_id)
    content['category'] = category

    products = Product.objects.filter(category=category)
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    content['products'] = products


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
    reviews = PenReview.objects.filter(product=product).order_by('-pub_date')
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    content['reviews'] = reviews

    # 태그 관련
    tags = set()
    for review in reviews:
        for tag in review.tags.all():
            tags.add(tag)

    content['tags'] = tags

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


@login_required(login_url='/account/logIn/')
def productRequest_view(request):
    requestLists = ProductRequest.objects.filter(author=request.user)
    return render(request, 'productRequest.html', {'requestLists':requestLists})


@login_required(login_url='/account/logIn/')
def newProductRequest_view(request):
    if request.method == 'POST':
        form = NewProductRequestForm(request.POST)
        if form.is_valid():
            newProductRequest :ProductRequest = form.save(commit=False)
            newProductRequest.author = request.user
            newProductRequest.save()
            
            return redirect('productRequestList')

    else:
        form = NewProductRequestForm()
        return render(request, 'newProductRequest.html', {'form':form})


@login_required(login_url='/account/logIn/')
def productRequestDetail_view(request, product_request_id):
    productRequest = get_object_or_404(ProductRequest, pk=product_request_id)
    return render(request, 'productRequestDetail.html', {'productRequest':productRequest})
    

@login_required(login_url='/account/logIn/')
def productRequestModify_view(request, product_request_id):
    return render(request, 'productRequestModify.html')


def rateBackUp_view(request):
    return render(request, 'rateBackUp.html')


def connectTagToReview(review:Review):
    rawTagString = review.rawTagString
    rawTags = rawTagString.split(' ')
    existTags = ReviewTag.objects.all()

    for newTagName in rawTags:
        if len(newTagName) > 15 : continue

        alreadyExists = False
        for existTag in existTags:
            if existTag.tag == newTagName:
                alreadyExists = True
                break
        
        if not alreadyExists:
            print(newTagName + " 태그가 존재하지 않아 새로 생성합니다.")
            newTag = ReviewTag.objects.create(tag=newTagName)
            review.tags.add(newTag)
            newTag.targetReview.add(review)
        else:
            existTag = ReviewTag.objects.get(tag=newTagName)
            review.tags.add(existTag)
            existTag.targetReview.add(review)


@login_required(login_url='/account/logIn/')
def reviewCreate_view(request, product_id):
    if request.method == 'POST':
        form = PenReviewForm(request.POST, request.FILES)

        product = Product.objects.get(pk=product_id)
        new_review : PenReview = form.save()
        new_review.product = product
        new_review.author = request.user
        new_review.pub_date = timezone.now()
        new_review.comment = request.POST['comment']
        new_review.goodPoint = request.POST['goodPoint']
        new_review.weakPoint = request.POST['weakPoint']
        new_review.rawTagString = request.POST['rawTagString']
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

        # 리뷰의 태그를 rawString으로부터 추출/연결
        connectTagToReview(new_review)

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
    # 한줄평
    content['comment'] = review.comment
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

    # 상품 태그 목록
    productTags = review.tags.all()
    content['productTags'] = productTags

    # 사용자 태그 목록
    userTags = review.author.tags.all()
    content['userTags'] = userTags

    # 댓글 목록
    comments = Comment.objects.filter(review=review).order_by('-pub_date')
    content['comments'] = comments

    return render(request, 'reviewDetail.html', content)


@login_required(login_url='/account/logIn/')
def reviewModify_view(request, review_id):
    content = dict()

    review = get_object_or_404(PenReview, pk=review_id)
    content['review'] = review

    return render(request, 'reviewModify.html', content)


def modifyReviewTags(review:PenReview):
    currentRawTagString = review.rawTagString
    currentTagNames = currentRawTagString.split(' ')
    existTags = set(list(obj.tag for obj in review.tags.all()))

    for name in currentTagNames:
        # 15자를 넘기는 태그이면 그냥 넘어감
        if len(name) > 15 : continue

        # 이미 존재하는 태그인 경우 삭제될 태그가 아니므로 existTags에서 삭제하고 넘어감
        if name in existTags :
            existTags.remove(name)
            continue

        # 새로운 태그가 추가된 경우
        if name not in existTags:
            newTag = ReviewTag.objects.create(tag=name)
            newTag.targetReview.add(review)
            review.tags.add(newTag)
    
    # 선택받지 못한? 태그들을 리뷰와 떼어놓음
    for tag in existTags:
        tag = ReviewTag.objects.get(tag=tag)
        tag.targetReview.remove(review)
        review.tags.remove(tag)
        tag.save()

    review.save()


@login_required(login_url='/account/logIn/')
def reviewUpdate(request, review_id):
    review : PenReview = get_object_or_404(PenReview, pk=review_id)

    review.pub_date = timezone.datetime.now()
    review.goodPoint = request.POST['goodPoint']
    review.weakPoint = request.POST['weakPoint']
    review.rawTagString = request.POST['rawTagString']

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

    modifyReviewTags(review)

    review.save()

    return redirect('/store/reviewDetail/' + str(review.id))


@login_required(login_url='/account/logIn/')
def reviewDelete(request, review_id):
    review : PenReview = get_object_or_404(PenReview, pk=review_id)
    product_id = review.product.id

    review.delete()

    return redirect('/store/productDetail/' + str(product_id))

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
def commentCreate(request, review_id):
    new_comment = Comment(
        author=request.user, pub_date=timezone.datetime.now(),
        review=PenReview.objects.get(pk=review_id), body=request.POST['body']
    )

    new_comment.save()

    return redirect('/store/reviewDetail/' + str(review_id))

@login_required(login_url='/account/logIn/')
def commentDelete(request, comment_id):
    target_comment : Comment = get_object_or_404(Comment, pk=comment_id)
    review_id : PenReview = target_comment.review.id
    target_comment.delete()

    return redirect('/store/reviewDetail/' + str(review_id))


def searchMain_view(request):
    return render(request, 'searchMain.html')


def getTopRelatedReviews(countLimit, rawTagString:str):
    inputTagNames = set(rawTagString.split(' '))
    reviews = PenReview.objects.all()

    productTagPair = dict()

    for review in reviews:
        product = review.product
        if product not in productTagPair:
            productTagPair[product] = getTagNames(review)
        else:
            productTagPair[product].update(getTagNames(review))


    for product, tagSet in productTagPair.items():
        productTagPair[product] = len(inputTagNames & tagSet)

    tagSimilarity = list((product, count) for product, count in productTagPair.items())
    tagSimilarity.sort(key=lambda pair: pair[1], reverse=True)

    return tagSimilarity[:countLimit]


def getTagNames(review:Review):
    tags = review.tags.all()
    result = set()

    for tag in tags:
        result.add(tag.tag)

    return result


def searchResult_view(request):
    class Pair:
        def __init__(self, product, cnt):
            self.product = product
            self.cnt = cnt

    content = dict()

    isKeywordSearch = False

    keywordQuery = request.GET['keywordQuery']
    if keywordQuery:
        searchResult = Product.objects.filter(name__contains=keywordQuery)
        statusMessage = f"키워드 검색 결과 {len(searchResult)}개의 제품이 검색되었습니다."
        isKeywordSearch = True
        content['searchResult'] = searchResult
        content['statusMessage'] = statusMessage

    else:
        tagQuery = request.GET['tagQuery']
        if tagQuery:
            similarityPair = getTopRelatedReviews(20, tagQuery)
            statusMessage = f"태그 검색 결과"
            
            searchResult = list(Pair(similarityPair[i][0], similarityPair[i][1]) for i in range(len(similarityPair)))
            content['searchResult'] = searchResult

            content['statusMessage'] = statusMessage

        else:
            searchResult = []
            statusMessage = "검색어를 입력해 주세요!"
            content['searchResult'] = searchResult
            content['statusMessage'] = statusMessage

    searchFailed = (len(searchResult) == 0)
    content['searchFailed'] = searchFailed
    
    content['isKeywordSearch'] = isKeywordSearch

    return render(request, 'searchResult.html', content)


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

def mainPage_view(request):
    content = dict()

    # 테스트/개발용이므로 서비스 할 때는 빠져아 함
    # 카테고리가 존재하지 않는 경우에만 하단의 모든 카테고리를 새로 생성하는 역할
    initializeCategory()
    # 랜덤으로 countLimit개까지 Product를 생성하고 임의로 카테고리를 지정
    automativeFilling_Product(countLimit=300)

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

def randomLike(request):
    # 로그인 되어 있을 경우 제품과 리뷰에 랜덤하게 좋아요를 누름
    likeProcess_RandomProducts(request, 50)
    likeProcess_RandomReviews(request, 50)

    return redirect('mainPage')