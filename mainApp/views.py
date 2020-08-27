from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet

from django.core.paginator import Paginator

from .models import *
from account.models import CustomerTag

from .forms import *

from .tools import *
from kakaoMapApp.tools import *

from .recommendation import *

from random import choice


def intro_view(request):
    return render(request, 'intro.html')


def productList_view(request, category_id):
    content = dict()

    category = ProductCategory.objects.get(pk=category_id)
    content['category'] = category

    try:
        sortBy = request.GET['sort']
        # 기본값 : 인기순 정렬
        if sortBy == 'popularity':
            products = Product.objects.filter(category=category).order_by('-likeCount')
            content['sortBy'] = 'popularity'
            popularitySort = True
        # 기타 : 최신순 정렬
        else:
            products = Product.objects.filter(category=category).order_by('-registerDate')
            content['sortBy'] = 'new'
            popularitySort = False
    except:
        products = Product.objects.filter(category=category).order_by('-likeCount')
        popularitySort = True


    content['popularitySort'] = popularitySort

    paginator = Paginator(products, 8)
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
    if len(videoLinkHashs) != 0:
        content['firstVideoHash'] = videoLinkHashs[0]
        content['videoLinkHashs'] = videoLinkHashs[1:]
        content['hasNoVideos'] = False
    else:
        content['hasNoVideos'] = True

    # 리뷰 관련
    # 인기순 정렬인 경우
    try:
        popularitySort = request.GET['sort']
        if popularitySort == 'popularity':
            content['popularitySort'] = True
            reviews = PenReview.objects.filter(product=product).order_by('-likeCount')
            content['sortBy'] = 'popularity'
        else:
            content['popularitySort'] = False
            reviews = PenReview.objects.filter(product=product).order_by('-pub_date')
            content['sortBy'] = 'new'
    # 혹시 몰라서,, 기본 정렬 방식을 인기순으로 예외처리
    except:
        content['popularitySort'] = True
        reviews = PenReview.objects.filter(product=product).order_by('-likeCount')
        content['sortBy'] = 'popularity'

    content['hasReviews'] = (len(reviews) > 0)

    # 평점 관련
    try:
        avr_totalScore = sum(list(map(lambda x: x.totalScore, reviews))) / len(reviews)
        content['avr_totalScore'] = avr_totalScore

        avr_gripScore = sum(list(map(lambda x: x.grip.score, reviews))) / len(reviews)
        content['avr_gripScore'] = avr_gripScore

        avr_lifeScore = sum(list(map(lambda x: x.life.score, reviews))) / len(reviews)
        content['avr_lifeScore'] = avr_lifeScore

        avr_durabilityScore = sum(list(map(lambda x: x.durability.score, reviews))) / len(reviews)
        content['avr_durabilityScore'] = avr_durabilityScore

        avr_designScore = sum(list(map(lambda x: x.design.score, reviews))) / len(reviews)
        content['avr_designScore'] = avr_designScore

        avr_textureScore = sum(list(map(lambda x: x.texture.score, reviews))) / len(reviews)
        content['avr_textureScore'] = avr_textureScore

        avr_costEffetivenessScore = sum(list(map(lambda x: x.costEffetiveness.score, reviews))) / len(reviews)
        content['avr_costEffetivenessScore'] = avr_costEffetivenessScore
    except:
        content['avr_totalScore'] = 0
        content['avr_gripScore'] = 0
        content['avr_lifeScore'] = 0
        content['avr_durabilityScore'] = 0
        content['avr_designScore'] = 0
        content['avr_textureScore'] = 0
        content['avr_costEffetivenessScore'] = 0


    # 리뷰를 작성한 적이 있는가?
    try:
        myReview = list(filter(lambda r: r.author == request.user, reviews))
        reviewCreated = (len(myReview) > 0)
        content['reviewCreated'] = reviewCreated
        
        myReview = list(filter(lambda r: r.author == request.user, reviews))[0]
        content['myReview'] = myReview

    except:
        content['reviewCreated'] = False


    paginator = Paginator(reviews, 8)
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    content['reviews'] = reviews

    # 태그 관련
    tags = set()
    for review in reviews:
        for tag in review.tags.all():
            tags.add(tag)

    content['tags'] = tags

    # 웹 판매정보 목록
    webSellInfoList = WebSellInfo.objects.filter(product=product).order_by('price')
    content['webSellInfoList'] = webSellInfoList
    if len(webSellInfoList) > 0:
        cheapestWebPrice = min(webSellInfoList, key=lambda info: info.price).price
        content['cheapestWebPrice'] = cheapestWebPrice
    try:
        webSellInfoRegistered = False
        targetWebSellInfo = None
        for info in webSellInfoList:
            if info.seller == request.user:
                webSellInfoRegistered = True
                targetWebSellInfo = info
                break
        content['webSellInfoRegistered'] = webSellInfoRegistered
        content['targetWebSellInfo'] = targetWebSellInfo

    except:
        content['webSellInfoRegistered'] = False
        content['targetWebSellInfo'] = None

    # 웹 판매정보가 있는지 표시
    hasWebSellInfo = len(webSellInfoList) > 0
    content['hasWebSellInfo'] = hasWebSellInfo

    # 문구점 판매정보 목록
    stationerSellInfoList = StationerSellInfo.objects.filter(product=product)
    content['stationerSellInfoList'] = stationerSellInfoList
    if len(stationerSellInfoList) > 0:
        cheapestStationerPrice = min(stationerSellInfoList, key=lambda info: info.price).price
        content['cheapestStationerPrice'] = cheapestStationerPrice

    try:
        stationerSellInfoRegistered = False
        targetStationerInfo = None
        for info in stationerSellInfoList:
            if info.seller == request.user:
                stationerSellInfoRegistered = True
                targetStationerInfo = info
                break
        content['stationerSellInfoRegistered'] = stationerSellInfoRegistered
        content['targetStationerInfo'] = targetStationerInfo

    except:
        content['webSellInfoRegistered'] = False
        content['targetStationerInfo'] = None

    # 등록된 문구점 판매정보가 없다면 지도를 표시할 수 없으므로 표시해놓음
    hasStationerSellInfo = len(stationerSellInfoList) > 0
    content['hasStationerSellInfo'] = hasStationerSellInfo

    # 지도 관련
    # 판매정보가 있다면?
    # -> 판매정보가 없는 경우 지도가 표시되지 않으므로(hasStationerSellInfo가 False이므로) 중심좌표를 입력될 필요 없다.
    if hasStationerSellInfo:
        # 위치정보가 정의되지 않는 WebSeller라면
        try:
            if request.user.is_WebSeller:
                # 등록된 판매정보 중 임의로 골라 중앙으로 설정
                randInfo = choice(stationerSellInfoList)
                centerLatLon = centerLatitude, centerLongitude = randInfo.seller.latitude, randInfo.seller.longitude
                zoomLevel = getZoomLevel(centerLatLon, stationerSellInfoList)
                content['zoomLevel'] = zoomLevel
                content['nullLocation'] = False
                content['centerLatitude'], content['centerLongitude'] = centerLatLon

            # 위치정보가 정의되는 Stationer/Customer라면
            else:
                # 만약 위치정보를 설정하지 않았다면
                if (request.user.latitude == 0 and request.user.longitude == 0):
                    # 지도를 표시하지 않을 것이므로 중심좌표 설정 X
                    content['nullLocation'] = True
                # 만약 위치정보를 설정했다면
                else:
                    # 중심좌표를 등록된 위치로 설정
                    centerLatLon = centerLatitude, centerLongitude = request.user.latitude, request.user.longitude
                    zoomLevel = getZoomLevel(centerLatLon, stationerSellInfoList)
                    content['zoomLevel'] = zoomLevel
                    content['nullLocation'] = False


                    content['centerLatitude'], content['centerLongitude'] = centerLatLon
        except:
            randInfo = choice(stationerSellInfoList)
            centerLatLon = centerLatitude, centerLongitude = randInfo.seller.latitude, randInfo.seller.longitude
            zoomLevel = getZoomLevel(centerLatLon, stationerSellInfoList)
            content['zoomLevel'] = zoomLevel
            content['nullLocation'] = False
            content['centerLatitude'], content['centerLongitude'] = centerLatLon
    

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
    content = dict()
    
    productRequests = ProductRequest.objects.filter(author=request.user)
    content['productRequests'] = productRequests

    hasRequests = (len(productRequests) > 0)
    content['hasRequests'] = hasRequests

    return render(request, 'productRequest.html', content)


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
    productRequest = get_object_or_404(ProductRequest, pk=product_request_id)
    if request.method == 'POST':
        form = NewProductRequestForm(request.POST, instance=productRequest)
        if form.is_valid():
            newProductRequest : ProductRequest = form.save(commit=False)
            newProductRequest.author = request.user
            newProductRequest.save()
            return redirect('productRequestList')

    else:
        form = NewProductRequestForm(instance=productRequest)
        return render(request, 'productRequestModify.html', {'form':form})


@login_required(login_url='/account/logIn/')
def productRequestDelete_view(request, product_request_id):
    delete_request = get_object_or_404(ProductRequest, pk=product_request_id)
    delete_request.delete()
    return redirect('productRequestList')


def connectTagToReview(review:Review):
    rawTagString = review.rawTagString
    rawTags = rawTagString.split(' ')
    existTags = ReviewTag.objects.all()

    for newTagName in rawTags:
        # 15자가 넘으면 버린다
        if len(newTagName) > 15 : continue

        alreadyExists = False
        for existTag in existTags:
            if existTag.tag == newTagName:
                alreadyExists = True
                break
        
        # 존재하는 태그가 아니라면
        if not alreadyExists:
            print(newTagName + " 태그가 존재하지 않아 새로 생성합니다.")
            newTag = ReviewTag.objects.create(tag=newTagName)
            review.tags.add(newTag)
            newTag.targetReview.add(review)
            newTag.save()
        else:
            existTag = ReviewTag.objects.get(tag=newTagName)
            review.tags.add(existTag)
            existTag.targetReview.add(review)
            existTag.save()
        
        review.save()
        # 태그 목록 갱신
        existTags = ReviewTag.objects.all()
    
    review.save()


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

        scores = [new_review.grip, new_review.life, new_review.durability, new_review.design, new_review.texture, new_review.costEffetiveness]
        new_review.totalScore = sum(map(lambda x: x.score, scores)) / len(scores)

        new_review.save()

        # 리뷰 이미지를 하나도 올리지 않았다면 대상 제품의 대표 이미지로 변경
        if not hasImageField(new_review):
            new_review.reviewImage1 = product.productImage
            new_review.save()

        # 리뷰의 태그를 rawString으로부터 추출/연결
        connectTagToReview(new_review)

        return redirect('productDetail', product_id=product_id)

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
    content['hasUserTags'] = (len(userTags) != 0)
    content['userTags'] = userTags
    print(userTags)

    # 댓글 목록
    comments = Comment.objects.filter(review=review).order_by('-pub_date')
    content['comments'] = comments

    #사진 목록
    images = [review.reviewImage1, review.reviewImage2, review.reviewImage3, review.reviewImage4, review.reviewImage5, review.reviewImage6]
    images = list(filter(lambda x: x, images))

    firstImage = images.pop(0)
    content['firstImage'] = firstImage
    content['images'] = images
    
    # 사진을 추가할 수 있는가?(사진이 6장 미만 등록되어 있는가?)
    imageCnt = len(list(filter(lambda x: x, images))) + 1
    content['imageLeft'] = 6 - imageCnt
    canAddImage = imageCnt < 6
    content['canAddImage'] = canAddImage

    # 사진을 추가로 받는 form
    newImageForm = ReviewImageAddForm()
    content['newImageForm'] = newImageForm

    return render(request, 'reviewDetail.html', content)


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
    rawTagString_before = review.rawTagString
    review.rawTagString = request.POST['rawTagString']

    review.grip.score = int(request.POST['grip'])
    review.grip.save()

    review.life.score = int(request.POST['life'])
    review.life.save()

    review.durability.score = int(request.POST['durability'])
    review.durability.save()

    review.design.score = int(request.POST['design'])
    review.design.save()

    review.texture.score = int(request.POST['texture'])
    review.texture.save()

    review.costEffetiveness.score = int(request.POST['costEffetiveness'])
    review.costEffetiveness.save()

    scores = [review.grip, review.life, review.durability, review.design, review.texture, review.costEffetiveness]
    review.totalScore = sum(map(lambda x: x.score, scores)) / len(scores)

    review.modified = True

    review.save()

    modifyReviewTags(review, rawTagString_before)

    review.save()

    return redirect('/store/reviewDetail/' + str(review.id))


@login_required(login_url='/account/logIn/')
def reviewImageAdd(request, review_id):
    form = ReviewImageAddForm(request.POST, request.FILES)

    review = PenReview.objects.get(pk=review_id)
    tmp = form.save(commit=False)
    if tmp.reviewImage1 is not None:
        images = [review.reviewImage1, review.reviewImage2, review.reviewImage3, review.reviewImage4, review.reviewImage5, review.reviewImage6]
        for i in range(len(images)):
            if images[i]:
                continue
            else:
                exec(f"review.reviewImage{i+1} = tmp.reviewImage1")
                break
        review.modified = True
        review.save()
    images = [review.reviewImage1, review.reviewImage2, review.reviewImage3, review.reviewImage4, review.reviewImage5, review.reviewImage6]

    return redirect('reviewDetail', review_id=review_id)


@login_required(login_url='/account/logIn/')
def reviewImageModify_view(request, review_id, imageURL):
    if request.method == "POST":
        form = ReviewImageModifyingForm(request.POST, request.FILES)

        review = PenReview.objects.get(pk=review_id)
        tmp = form.save(commit=False)
        if tmp.reviewImage1 is not None:
            targetIdx = -1
            images = [review.reviewImage1, review.reviewImage2, review.reviewImage3, review.reviewImage4, review.reviewImage5, review.reviewImage6]
            for i in range(len(images)):
                if images[i].url == imageURL:
                    targetIdx = i
                    break
            exec(f"review.reviewImage{targetIdx+1} = tmp.reviewImage1")
            review.modified = True
            review.save()

        return redirect('reviewDetail', review_id=review_id)

    else:
        content = dict()
        
        form = ReviewImageModifyingForm()
        content['form'] = form

        review = PenReview.objects.get(pk=review_id)
        content['review'] = review

        targetIdx = -1
        images = [review.reviewImage1, review.reviewImage2, review.reviewImage3, review.reviewImage4, review.reviewImage5, review.reviewImage6]
        for i in range(len(images)):
            if images[i].url == imageURL:
                targetIdx = i
                break

        targetImage = eval(f"review.reviewImage{i+1}")
        content['targetImage'] = targetImage

        return render(request, 'reviewImageModify.html', content)

@login_required(login_url='/account/logIn/')
def firstReviewImageModify_view(request, review_id):
    if request.method == "POST":
        form = ReviewImageModifyingForm(request.POST, request.FILES)

        review = PenReview.objects.get(pk=review_id)
        tmp = form.save(commit=False)
        if tmp.reviewImage1 is not None:
            firstImageIdx = -1
        
            images = [review.reviewImage2, review.reviewImage3, review.reviewImage4, review.reviewImage5, review.reviewImage6]
            for i in range(len(images)):
                if images[i]:
                    firstImageIdx = i
                    break
            
            if i == -1:
                review.reviewImage1 = tmp.reviewImage1
            else:
                exec(f"review.reviewImage{firstImageIdx+2} = tmp.reviewImage1")

            review.modified = True
            review.save()

        return redirect('reviewDetail', review_id=review_id)

    else:
        content = dict()

        form = ReviewImageModifyingForm()
        content['form'] = form

        review = PenReview.objects.get(pk=review_id)
        content['review'] = review

        content['image'] = review.getMainImage()

        return render(request, 'firstReviewImageModify.html', content)


@login_required(login_url='/account/logIn/')
def firstReviewImageDelete(request, review_id):
    review : PenReview = PenReview.objects.get(pk=review_id)
    review.modified = True

    firstImageIdx = -1
    images = [review.reviewImage2, review.reviewImage3, review.reviewImage4, review.reviewImage5, review.reviewImage6]
    for i in range(len(images)):
        if images[i]:
            firstImageIdx = i
            break
    
    if i == -1:
        review.reviewImage1 = None
    else:
        exec(f"review.reviewImage{firstImageIdx+2} = None")

    if not hasImageField(review):
        review.reviewImage1 = review.product.productImage

    review.save()

    return redirect('reviewDetail', review_id=review_id)


def reviewsByTag_view(request, tagName:str):
    content = dict()

    content['tagName'] = tagName

    tags = CustomerTag.objects.filter(tagBody=tagName)
    reviewers = set()
    for tag in tags:
        for user in tag.targetCustomer.all():
            reviewers.add(user)
    
    reviews = list()
    for reviewer in reviewers:
        for review in PenReview.objects.filter(author=reviewer):
            reviews.append(review)
    
    reviews.sort(key=lambda x: x.likeCount, reverse=True)

    paginator = Paginator(reviews, 8)
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    content['reviews'] = reviews

    content['reviewerNumber'] = len(reviewers)
    content['reviewNumber'] = len(reviews)

    content['solo'] = (len(reviewers) == 1)
    if len(reviewers) == 1:
        content['soloReviewer'] = reviewers.pop()

    return render(request, 'reviewsByTag.html', content)


@login_required(login_url='/account/logIn/')
def reviewImageDelete(request, review_id, imageURL):
    review : PenReview = PenReview.objects.get(pk=review_id)
    review.modified = True

    targetIdx = -1
    images = [review.reviewImage1, review.reviewImage2, review.reviewImage3, review.reviewImage4, review.reviewImage5, review.reviewImage6]
    for i in range(len(images)):
        print(images[i].url, "|", imageURL)
        if images[i].url == imageURL:
            targetIdx = i
            break

    exec(f"review.reviewImage{i+1}=None")

    if not hasImageField(review):
        review.reviewImage1 = review.product.productImage

    review.save()

    return redirect('reviewDetail', review_id=review_id)


def modifyReviewTags(review:PenReview, before:str):
    newRawTagString = review.rawTagString
    newTagNames = set(newRawTagString.split(' '))

    beforeRawTagString = before

    tagNames_toRemove = set(beforeRawTagString.split(' ')) - newTagNames
    tagNames_toAdd = newTagNames - set(beforeRawTagString.split(' '))

    for name in tagNames_toRemove:
        targetTags = ReviewTag.objects.filter(tag=name)
        for tag in targetTags:
            tag.targetReview.remove(review)
            review.tags.remove(tag)

            tag.save()
            review.save()
            
            if len(tag.targetReview.all()) == 0:
                tag.delete()
            
    tag_namespace = set(map(lambda x: x.tag, ReviewTag.objects.all()))
    for name in tagNames_toAdd:
        if name not in tag_namespace:
            newTag : ReviewTag = ReviewTag.objects.create(tag=name)
            newTag.targetReview.add(review)
            newTag.save()
            review.tags.add(newTag)
            review.save()
        else:
            existTag : ReviewTag = ReviewTag.objects.get(tag=name)
            existTag.targetReview.add(review)
            existTag.save()
            review.tags.add(existTag)
            review.save()
    
    review.save()


def unconnectTags(review_id):
    review : PenReview = get_object_or_404(PenReview, pk=review_id)
    tags = review.tags.all()

    for tag in tags:
        tag.targetReview.remove(review)
        if len(tag.targetReview.all()) == 0:
            tag.delete()
        tag.save()
    
    review.save()


@login_required(login_url='/account/logIn/')
def reviewDelete(request, review_id):
    review : PenReview = get_object_or_404(PenReview, pk=review_id)
    product_id = review.product.id

    unconnectTags(review_id)

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
    content = dict()

    content['error'] = False
    content['ERROR_MESSAGE'] = ""

    return render(request, 'searchMain.html', content)


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

    result = list(filter(lambda pair: pair[1] != 0, tagSimilarity))
    result.sort(key=lambda pair: pair[1], reverse=True)

    return result[:countLimit]


def getTagNames(review:Review):
    tags = review.tags.all()
    result = set()

    for tag in tags:
        result.add(tag.tag)

    return result


def keywordSearchResult_view(request):
    content = dict()

    keywordQuery = request.GET['keywordQuery']
    popularitySort = request.GET['sort']

    if keywordQuery:
        
        popularitySort = (popularitySort == 'popularity')
        content['popularitySort'] = popularitySort
        # Product
        # 제품명으로 검색
        searchResult_productName = Product.objects.filter(name__contains=keywordQuery)
        # 제조사로 검색
        searchResult_manufacturer = Product.objects.filter(manufacturer__contains=keywordQuery)
        # 제품 설명으로 검색
        searchResult_description = Product.objects.filter(description__contains=keywordQuery)

        searchResult = list(searchResult_productName | searchResult_manufacturer | searchResult_description)

        # PenReview
        # 리뷰 한줄평으로 검색
        searchResult_reviewComment = PenReview.objects.filter(comment__contains=keywordQuery)
        # 리뷰 장점으로 검색
        searchResult_goodPoint = PenReview.objects.filter(goodPoint__contains=keywordQuery)
        # 리뷰 단점으로 검색
        searchResult_weakPoint = PenReview.objects.filter(weakPoint__contains=keywordQuery)

        # 검색된 리뷰들이 가리키는 제품을 searchResult에 가져옴
        searchedReviews = searchResult_reviewComment | searchResult_goodPoint | searchResult_weakPoint
        for review in searchedReviews:
            if review.product not in searchedReviews:
                searchResult.append(review.product)

        # 정렬 | 기본값 : 시간
        if popularitySort:
            searchResult.sort(key=lambda x: x.likeCount)
        else:
            searchResult.sort(key=lambda x: x.registerDate, reverse=True)

        statusMessage = f"키워드 검색 결과 {len(searchResult)}개의 제품이 검색되었습니다."
        content['searchResult'] = searchResult
        content['statusMessage'] = statusMessage
        content['keywordQuery'] = keywordQuery


    else:
        content = dict()
        content['error'] = True
        content['ERROR_MESSAGE'] = "검색어를 입력해 주세요!"
        return render(request, 'searchMain.html', content)
    
    return render(request, 'keywordSearchResult.html', content)


def tagSearchResult_view(request):
    class Pair:
        def __init__(self, product, cnt):
            self.product = product
            self.cnt = cnt

    content = dict()

    tagQuery = request.GET['tagQuery']

    if tagQuery:
        if tagQuery:
            similarityPair = getTopRelatedReviews(20, tagQuery)
            statusMessage = f"태그 검색 결과 {len(similarityPair)}개의 제품이 검색되었습니다."
            
            searchResult = list(Pair(similarityPair[i][0], similarityPair[i][1]) for i in range(len(similarityPair)))
            content['searchResult'] = searchResult
            content['statusMessage'] = statusMessage

    else:
        content = dict()
        content['error'] = True
        content['ERROR_MESSAGE'] = "검색어를 입력해 주세요!"
        return render(request, 'searchMain.html', content)
    
    return render(request, 'tagSearchResult.html', content)


@login_required(login_url='/account/logIn/')
def stationerSellInfoCreate_view(request, product_id):
    if request.method == 'POST':
        form = StationerSellInfoForm(request.POST)
        new_sellInfo : StationerSellInfo = form.save(commit=False)
        new_sellInfo.product = Product.objects.get(pk=product_id)
        new_sellInfo.seller = request.user

        new_sellInfo.save()

        return redirect('productDetail', product_id=product_id)

    else:
        content = dict()
        
        # 위치정보를 입력하지 않았으면(위도 경도가 기본값 : 0이면) 이용 불가능
        userInstance : Customer = request.user
        content['nullLocation'] = (userInstance.latitude == 0 and userInstance.longitude == 0)

        product = Product.objects.get(pk=product_id)
        content['product'] = product

        try:
            stationerSellInfos = StationerSellInfo.objects.filter(product=product)

        except:
            stationerSellInfos = []

        alreadyExists = False
        for info in stationerSellInfos:
            if info.seller == request.user:
                createdInfo = info
                content['createdInfo'] = createdInfo
                alreadyExists = True
                break

        content['alreadyExists'] = alreadyExists
        form = StationerSellInfoForm()
        content['form'] = form

        return render(request, 'stationerSellInfoCreate.html', content)


@login_required(login_url='/account/logIn/')
def stationerSellInfoModify_view(request, product_id, stationerSellInfo_id):
    stationerSellInfo : StationerSellInfo = get_object_or_404(StationerSellInfo, pk=stationerSellInfo_id)

    if request.method == "POST":
        form = StationerSellInfoForm(request.POST)
        if form.is_valid():
            stationerSellInfo.price = form.cleaned_data['price']
            stationerSellInfo.save()

            return redirect('productDetail', product_id=product_id)
    
    else:
        content = dict()
        
        form = StationerSellInfoForm()
        content['form'] = form

        currentPrice = stationerSellInfo.price
        content['currentPrice'] = currentPrice

        product = stationerSellInfo.product
        content['product'] = product

        return render(request, 'stationerSellInfoModify.html', content)


@login_required(login_url='/account/logIn/')
def stationerSellInfoDelete(request, product_id, stationerSellInfo_id):
    targetInfo = get_object_or_404(StationerSellInfo, pk=stationerSellInfo_id)
    targetInfo.delete()

    return redirect('productDetail', product_id=product_id)


@login_required(login_url='/account/logIn/')
def webSellInfoCreate_view(request, product_id):
    if request.method == 'POST':
        form = WebSellInfoForm(request.POST)
        new_sellInfo : WebSellInfo = form.save(commit=False)
        new_sellInfo.product = Product.objects.get(pk=product_id)
        new_sellInfo.seller = request.user
        
        new_sellInfo.save()

        return redirect('productDetail', product_id=product_id)
    
    else:
        content = dict()

        product = Product.objects.get(pk=product_id)
        content['product'] = product

        try:
            webSellInfos = WebSellInfo.objects.filter(product=product)

        except:
            webSellInfos = []

        alreadyExists = False
        for info in webSellInfos:
            if info.seller == request.user:
                createdInfo = info
                content['createdInfo'] = createdInfo
                alreadyExists = True
                break

        content['alreadyExists'] = alreadyExists
        form = WebSellInfoForm()
        content['form'] = form

        return render(request, 'webSellInfoCreate.html', content)


@login_required(login_url='/account/logIn/')
def webSellInfoModify_view(request, product_id, webSellInfo_id):
    webSellInfo = get_object_or_404(WebSellInfo, pk=webSellInfo_id)

    if request.method == "POST":
        form = WebSellInfoForm(request.POST)
        if form.is_valid():
            webSellInfo.price = form.cleaned_data['price']
            webSellInfo.link = form.cleaned_data['link']
            webSellInfo.save()

            return redirect('productDetail', product_id=product_id)

    else:
        content = dict()

        form = WebSellInfoForm(instance=webSellInfo)
        content['form'] = form

        product = webSellInfo.product
        content['product'] = product

        return render(request, 'webSellInfoModify.html', content)


def tagProduct_view(request, productTag_id):
    content = dict()

    tag = ReviewTag.objects.get(pk=productTag_id)

    productList = set()
    for product in Product.objects.all():
        for review in PenReview.objects.filter(product=product):
            if tag in review.tags.all():
                productList.add(product)

    content['productList'] = productList
    content['length'] = len(productList)
    content['tag'] = tag.tag

    return render(request, 'tagProduct.html', content)


@login_required(login_url='/account/logIn/')
def webSellInfoDelete(request, product_id, webSellInfo_id):
    targetInfo = get_object_or_404(WebSellInfo, pk=webSellInfo_id)
    targetInfo.delete()

    return redirect('productDetail', product_id=product_id)


@login_required(login_url='/account/logIn/')
def userRecommendation_view(request):
    content = dict()
    content['error'] = False

    user = request.user
    topSimilarity = orderby_similarity(user)
    
    if len(topSimilarity) == 0:
        content['error'] = True

    content['topSimilarity'] = topSimilarity

    return render(request, 'userRecommendation.html', content)


def mainPage_view(request):
    content = dict()

    # 카테고리가 존재하지 않는 경우에만 하단의 모든 카테고리를 새로 생성하는 역할
    initializeCategory()

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

    # 새 리뷰
    newReviews = PenReview.objects.all().order_by('-pub_date')[:4]
    content['newReviews'] = newReviews

    # 인기 리뷰
    popularReviews = PenReview.objects.all().order_by('-likeCount')[:4]
    content['popularReviews'] = popularReviews
    
    # 맞춤 리뷰
    try:
        topSimilarity_pair = orderby_similarity(request.user, 1)
        topSimilarity_users = list(map(lambda pair: pair[0], topSimilarity_pair))
        content['error'] = (len(topSimilarity_users) == 0) # 리뷰를 작성한 적이 없거나, 자기와 겹치는 리뷰 성향이 없는 경우
        content['topSimilarity_users'] = topSimilarity_users
        content['topSimilarity_users_len'] = len(topSimilarity_users)

        topSimilarityReviews = list()
        for user in topSimilarity_users:
            topSimilarityReviews.append(PenReview.objects.filter(author=user).order_by('-likeCount')[:4])
        content['topSimilarityReviews'] = topSimilarityReviews

    except:
        content['error'] = True

    # 연령대 / 직업 / 주 사용 용도 중 1개 정보를 랜덤으로 골라
    # 해당 정보가 겹치는 리뷰어들의 리뷰를 보여주는 기능
    # + 관심 등록 펜 유형의 인기 리뷰를 보여주는 기능
    # 단, '기타'로 설정된 항목은 사용할 수 없으며
    # 3가지 정보가 모두 '기타'인 경우 해당 기능 전체를 사용할 수 없다.
    user : Customer = request.user

    # 당연히 로그인 하지 않은 유저는 해당 기능을 사용할 수 없다
    if user.is_authenticated:
        # 이하 연령대/직업/주사용용도 기반 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        user_age = ('age', user.age.__str__(), Customer.age_dict[user.age.__str__()])
        user_job = ('job', user.job.__str__(), Customer.job_dict[user.job.__str__()])
        user_usage = ('usage', user.usage.__str__(), Customer.usage_dict[user.usage.__str__()])
        userInfoList = list(filter(lambda x: x[-1] != '기타', [user_age, user_job, user_usage]))
        
        # 최소 1개 이상의 정보는 공개되어야 함
        propertyRecommend = (len(userInfoList) > 0)
        if propertyRecommend:
            picked = picked_field, picked_key, picked_val = random.choice(userInfoList)
            
            if picked_field == "age":
                picked_reviewers = Customer.objects.filter(age=user_age[1]).exclude(username=user.username)
                propertyMessage = f"{user_age[-1]} 리뷰어님들의 인기 리뷰입니다."
                content['propertyMessage'] = propertyMessage
            elif picked_field == "job":
                picked_reviewers = Customer.objects.filter(job=user_job[1]).exclude(username=user.username)
                propertyMessage = f"{user_job[-1]} 리뷰어님들의 인기 리뷰입니다."
                content['propertyMessage'] = propertyMessage
            elif picked_field == "usage":
                picked_reviewers = Customer.objects.filter(usage=user_usage[1]).exclude(username=user.username)
                propertyMessage = f"주 사용처가 {user_usage[-1]}인 리뷰어님들의 인기 리뷰입니다."
                content['propertyMessage'] = propertyMessage

            picked_reviews = list()
            for reviewer in picked_reviewers:
                for review in PenReview.objects.filter(author=reviewer):
                    picked_reviews.append(review)
            picked_reviews.sort(key=lambda x: x.likeCount, reverse=True)
            
            # 검색된 리뷰어들의 리뷰가 없으면(리뷰어가 검색되지 않는 경우에도 마찬가지) 기능 사용 불가
            if len(picked_reviews) == 0:
                propertyRecommend = False
            else:
                reviews_byProperty = picked_reviews[:4]
                content['reviews_byProperty'] = reviews_byProperty

        content['propertyRecommend'] = propertyRecommend

        # 이상 연령대/직업/주사용용도 기반 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # 이하 관심 펜 기반 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        userInterestPens = [(user.penInterest_1.__str__(), Customer.pen_dict[user.penInterest_1.__str__()]),
                            (user.penInterest_2.__str__(), Customer.pen_dict[user.penInterest_2.__str__()]),
                            (user.penInterest_3.__str__(), Customer.pen_dict[user.penInterest_3.__str__()])]
        userInterestPens = list(filter(lambda x: x[-1] != '기타', userInterestPens))

        # 최소 1개 이상의 관심 펜은 지정되어야 함
        penInterestRecommend = (len(userInterestPens) > 0)
        if penInterestRecommend:
            picked = picked_key, picked_val = random.choice(userInterestPens)

            picked_category = ProductCategory.objects.get(categoryName=picked_val)
            picked_pens = Product.objects.filter(category=picked_category)
            content['penInterestMessage'] = f"{picked_category.categoryName} 카테고리의 인기 리뷰입니다."

            picked_reviews = list()
            for pen in picked_pens:
                reviewList = PenReview.objects.filter(product=pen)
                for review in reviewList:
                    if review.author == user:
                        continue
                    picked_reviews.append(review)
            picked_reviews.sort(key=lambda x: x.likeCount, reverse=True)

            # 해당 카테고리에 펜이 없으면(또는 펜은 검색되는데 리뷰가 없으면) 기능 사용 불가
            if len(picked_reviews) == 0:
                penInterestRecommend = False
            else:
                reviews_byPenInterest = picked_reviews[:4]
                content['reviews_byPenInterest'] = reviews_byPenInterest
    
        content['penInterestRecommend'] = penInterestRecommend
            
    return render(request, 'mainPage.html', content)


def randomLike(request):
    # 로그인 되어 있을 경우 제품과 리뷰에 랜덤하게 좋아요를 누름
    likeProcess_RandomProducts(request, 50)
    likeProcess_RandomReviews(request, 50)

    return redirect('mainPage')
