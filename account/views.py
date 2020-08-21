from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout

from .forms import UserSignUpForm, UserLoginForm, WebSellerSignUpForm, StationerSignUpForm

from account.models import Customer, CustomerTag
from mainApp.models import *


def selectCustomerType_view(request):
    return render(request, 'selectCustomerType.html')


def connectTagToUser(user:Customer, rawString:str):
    # 일반 str문자열 : 띄어쓰기를 기준으로 태그 정보가 나누어져 있음
    rawTags = rawString.split(' ')
    # 현재 존재하는 태그의 목록
    existTags = CustomerTag.objects.all()
    
    # 새로 만들어질 태그가 이미 존재한다면 새로 생성하지 않는다.
    for newTagName in rawTags:
        if len(newTagName) > 10 : continue

        alreadyExists = False
        for existTag in existTags:
            if existTag.tagBody == newTagName:
                alreadyExists = True
                break
        
        if not alreadyExists:
            print(newTagName + " 태그가 존재하지 않아 새로 생성합니다.")
            newTag = CustomerTag.objects.create(tagBody=newTagName)
            user.tags.add(newTag)
            newTag.targetCustomer.add(user)
        else:
            existTag = CustomerTag.objects.get(tagBody=newTagName)
            user.tags.add(existTag)


def userSignUp_view(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            user.save()
            connectTagToUser(user, form.cleaned_data['rawTagString'])

            login(request, user)
            return redirect("setLocation")
        
        return render(request, 'userSignUp.html', {'form':form})


    else :
        form = UserSignUpForm()
        return render(request, 'userSignUp.html', {'form':form})


def webSellerSignUp_view(request):
    if request.method == 'POST':
        form = WebSellerSignUpForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            user.save()

            login(request, user)
            return redirect("mainPage")
        
        return render(request, 'webSellerSignUp.html', {'form':form})

    else :
        form = WebSellerSignUpForm()
        return render(request, 'webSellerSignUp.html', {'form':form})


def stationerSignUp_view(request):
    if request.method == 'POST':
        form = StationerSignUpForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("setLocation")
        
        return render(request, 'stationerSignUp.html', {'form':form})

    else :
        form = StationerSignUpForm()
        return render(request, 'stationerSignUp.html', {'form':form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request=request, username=username, password=password)

            if user is not None :
                login(request, user)
                return redirect("mainPage")

            return render(request, 'logIn.html', {'form':form})
            

    else :
        form = UserLoginForm()
        return render(request, 'logIn.html', {'form':form})


def logout_view(request):
    logout(request)
    return redirect("mainPage")


def modifyStationerSellInfo_view(request):
    return render(request, 'modifyStationerSellInfo.html')


def modifyUserInfo_view(request):
    return render(request, 'modifyUserInfo.html')


def modifyWebSellerInfo_view(request):
    return render(request, 'modifyWebSellerInfo.html')


@login_required(login_url='/account/logIn/')
def myPage_view(request):
    content = dict()
    
    user : Customer = request.user

    # 좋아요를 누른 리뷰 목록
    reviewList = PenReview.objects.all()
    likeReviewList = list()
    for review in reviewList:
        if user in review.likers.all():
            likeReviewList.append(review)
    content['likeReviewList'] = likeReviewList

    # 좋아요를 누른 제품 목록
    productList = Product.objects.all()
    likeProductList = list()
    for product in productList:
        if user in product.likers.all():
            likeProductList.append(product)
    content['likeProductList'] = likeProductList

    # 작성한 리뷰 목록
    myReviews = PenReview.objects.filter(author=user)
    content['myReviews'] = myReviews

    # 웹 판매정보 목록
    if user.is_WebSeller:
        webSellInfoList = WebSellInfo.objects.filter(seller=user)
    else:
        webSellInfoList = []
    content['webSellInfoList'] = webSellInfoList

    # 문구점 판매정보 목록
    if user.is_Stationer:
        stationerSellInfoList = StationerSellInfo.objects.filter(seller=user)
    else:
        stationerSellInfoList = []
    content['stationerSellInfoList'] = stationerSellInfoList

    return render(request, 'myPage.html', content)


def selectSellerType_view(request):
    return render(request, 'selectSellerType.html')


def setLocation_view(request):
    if request.method == "POST":
        try :
            coordinateTuple = eval(request.POST["rawLocation"])
            request.user.latitude = coordinateTuple[0]
            request.user.longitude = coordinateTuple[1]
            request.user.save()
            return redirect("mainPage")

        except:
            return render(request, 'setLocation.html', {'ERROR':True})

    return render(request, 'setLocation.html', {'ERROR':False})


def stationerSellInfoList_view(request):
    return render(request, 'stationerSellInfoList.html')


def webSellerInfoList_view(request):
    return render(request, 'webSellerInfoList.html')