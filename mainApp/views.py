from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from .models import *
from account.models import CustomerTag

from .forms import *

from .tools import *
from kakaoMapApp.tools import *

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
            popularitySort = True
        # 기타 : 최신순 정렬
        else:
            products = Product.objects.filter(category=category).order_by('-registerDate')
            popularitySort = False
    except:
        products = Product.objects.filter(category=category).order_by('-likeCount')
        popularitySort = True


    content['popularitySort'] = popularitySort

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
    # 인기순 정렬인 경우
    try:
        popularitySort = request.GET['sort']
        if popularitySort == 'popularity':
            content['popularitySort'] = True
            reviews = PenReview.objects.filter(product=product).order_by('-likeCount')
        else:
            content['popularitySort'] = False
            reviews = PenReview.objects.filter(product=product).order_by('-pub_date')
    # 혹시 몰라서,, 기본 정렬 방식을 인기순으로 예외처리
    except:
        content['popularitySort'] = True
        reviews = PenReview.objects.filter(product=product).order_by('-likeCount')

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

    # 웹 판매정보 목록
    webSellInfoList = WebSellInfo.objects.filter(product=product)
    content['webSellInfoList'] = webSellInfoList

    # 문구점 판매정보 목록
    stationerSellInfoList = StationerSellInfo.objects.filter(product=product)
    content['stationerSellInfoList'] = stationerSellInfoList

    # 등록된 문구점 판매정보가 없다면 지도를 표시할 수 없으므로 표시해놓음
    hasStationerSellInfo = len(stationerSellInfoList) > 0
    content['hasStationerSellInfo'] = hasStationerSellInfo

    # 지도 관련
    content['nullLocation'] = False
    # 판매정보가 있다면?
    # -> 판매정보가 없는 경우 지도가 표시되지 않으므로(hasStationerSellInfo가 False이므로) 중심좌표가 입력될 필요 없다.
    if hasStationerSellInfo:
        # 위치정보가 정의되지 않는 WebSeller라면
        if request.user.is_WebSeller:
            # 등록된 판매정보 중 임의로 골라 중앙으로 설정
            randInfo = choice(stationerSellInfoList)
            centerLatLon = centerLatitude, centerLongitude = randInfo.seller.latitude, randInfo.seller.longitude
            zoomLevel = getZoomLevel(centerLatLon, stationerSellInfoList)
            content['zoomLevel'] = zoomLevel
        
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

     content['centerLatitude'], content['centerLongitude'] = centerLatitude, centerLongitude
    

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
    productRequests = ProductRequest.objects.filter(author=request.user)
    return render(request, 'productRequest.html', {'productRequests':productRequests})


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

        scores = [new_review.grip, new_review.life, new_review.durability, new_review.design, new_review.texture, new_review.costEffetiveness, new_review.versatility]
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

    #사진 목록
    images = [review.reviewImage1, review.reviewImage2, review.reviewImage3, review.reviewImage4, review.reviewImage5, review.reviewImage6]
    content['images'] = images

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

    review.versatility.score = int(request.POST['versatility'])
    review.versatility.save()
    
    scores = [review.grip, review.life, review.durability, review.design, review.texture, review.costEffetiveness, review.versatility]
    review.totalScore = sum(map(lambda x: x.score, scores)) / len(scores)

    review.modified = True

    review.save()

    modifyReviewTags(review)

    review.save()

    return redirect('/store/reviewDetail/' + str(review.id))


@login_required(login_url='/account/logIn/')
def reviewImageModify_view(request, review_id, imageIdx):
    if request.method == "POST":
        form = ReviewImageModifyingForm(request.POST, request.FILES)

        review = PenReview.objects.get(pk=review_id)
        tmp = form.save(commit=False)
        if tmp.reviewImage1 is not None:
            exec(f"review.reviewImage{imageIdx+1} = tmp.reviewImage1")
            review.modified = True
            review.save()

        return redirect('reviewDetail', review_id=review_id)

    else:
        content = dict()

        form = ReviewImageModifyingForm()
        content['form'] = form

        review = PenReview.objects.get(pk=review_id)
        content['review'] = review

        content['imageIdx'] = imageIdx
        exec(f"content['image'] = review.reviewImage{imageIdx+1}")

        return render(request, 'reviewImageModify.html', content)


@login_required(login_url='/account/logIn/')
def reviewImageDelete(request, review_id, imageIdx):
    review : PenReview = PenReview.objects.get(pk=review_id)
    review.modified = True
    exec(f"review.reviewImage{imageIdx+1} = None")

    if not hasImageField(review):
        review.reviewImage1 = review.product.productImage

    review.save()

    return redirect('reviewDetail', review_id=review_id)


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
        if popularitySort == 'popularity':
            content['popularitySort'] = True
            searchResult = Product.objects.filter(name__contains=keywordQuery).order_by('likeCount')
        else:
            content['popularitySort'] = False
            searchResult = Product.objects.filter(name__contains=keywordQuery).order_by('-registerDate')

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
        # try:
        #     stationerSellInfos = StationerSellInfo.objects.get(product=product)
        # except:
        #     stationerSellInfos = []

        # alreadyExists = False
        # for info in stationerSellInfos:
        #     if info.seller == request.user:
        #         alreadyExists = True
        #         break

        # if alreadyExists:
        #     return redirect('productDetail', product_id=product_id)

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
        form = StationerSellInfoForm(instance=stationerSellInfo)
        return render(request, 'stationerSellInfoModify.html', {'form':form})


@login_required(login_url='/account/logIn/')
def stationerSellInfoDelete(request, product_id, stationerSellInfo_id):
    targetInfo = get_object_or_404(StationerSellInfo, pk=stationerSellInfo_id)
    targetInfo.delete()

    return redirect('productDetail', product_id=product_id)


@login_required(login_url='/account/logIn/')
def webSellInfoCreate_view(request, product_id):
    if request.method == 'POST':
        # try:
        #     webSellInfos = WebSellInfo.objects.get(product=product)

        # except:
        #     webSellInfos = []

        # alreadyExists = False
        # for info in webSellInfos:
        #     if info.seller == request.user:
        #         alreadyExists = True
        #         break

        # if alreadyExists:
        #     return redirect('productDetail', product_id=product_id)

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
        form = WebSellInfoForm(instance=webSellInfo)
        return render(request, 'webSellInfoModify.html', {'form':form})


@login_required(login_url='/account/logIn/')
def webSellInfoDelete(request, product_id, webSellInfo_id):
    targetInfo = get_object_or_404(WebSellInfo, pk=webSellInfo_id)
    targetInfo.delete()

    return redirect('productDetail', product_id=product_id)


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

    popularReviews = PenReview.objects.all().order_by('-likeCount')[:10]
    content['popularReviews'] = popularReviews
    

    return render(request, 'mainPage.html', content)


def randomLike(request):
    # 로그인 되어 있을 경우 제품과 리뷰에 랜덤하게 좋아요를 누름
    likeProcess_RandomProducts(request, 50)
    likeProcess_RandomReviews(request, 50)

    return redirect('mainPage')
