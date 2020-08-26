from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout

from .forms import *

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
            newTag = CustomerTag.objects.create(tagBody=newTagName)
            user.tags.add(newTag)
            newTag.targetCustomer.add(user)
        else:
            existTag = CustomerTag.objects.get(tagBody=newTagName)
            user.tags.add(existTag)


def modifyUserTag(user:Customer, before:str):
    newRawTagString = user.rawTagString
    newTagNames = set(newRawTagString.split(' '))

    beforeRawTagString = before

    tagNames_toRemove = set(beforeRawTagString.split(' ')) - newTagNames
    tagNames_toAdd = newTagNames -set(beforeRawTagString.split(' '))

    for name in tagNames_toRemove:
        targetTags = CustomerTag.objects.filter(tagBody=name)
        for tag in targetTags:
            tag.targetCustomer.remove(user)
            user.tags.remove(tag)

            tag.save()
            user.save()
            
            if len(tag.targetCustomer.all()) == 0:
                tag.delete()
            
    tag_namespace = set(map(lambda x: x.tagBody, CustomerTag.objects.all()))
    for name in tagNames_toAdd:
        if name not in tag_namespace:
            newTag : CustomerTag = CustomerTag.objects.create(tagBody=name)
            newTag.targetCustomer.add(user)
            newTag.save()
            user.tags.add(newTag)
            user.save()
        else:
            existTag : CustomerTag = CustomerTag.objects.get(tagBody=name)
            existTag.targetCustomer.add(user)
            existTag.save()
            user.tags.add(existTag)
            user.save()
    
    user.save()
    

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
            connectTagToUser(user, form.cleaned_data['rawTagString'])

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
            user.save()
            connectTagToUser(user, form.cleaned_data['rawTagString'])

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


@login_required(login_url='/account/logIn/')
def modifyUserInfo_view(request):
    if request.method == "POST":
        beforeString = request.user.rawTagString
        if request.user.is_Customer:
            form = UserModifyForm(request.POST, request.FILES, instance=request.user)
        elif request.user.is_Stationer:
            form = StationerModifyForm(request.POST, request.FILES, instance=request.user)
        elif request.user.is_WebSeller:
            form = WebSellerModifyForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()

            modifyUserTag(request.user, beforeString)

            return redirect('myPage')

    else:
        content = dict()

        if request.user.is_Customer:
            form = UserModifyForm(instance=request.user)
        elif request.user.is_Stationer:
            form = StationerModifyForm(instance=request.user)
        elif request.user.is_WebSeller:
            form = WebSellerModifyForm(instance=request.user)

        content['form'] = form

        return render(request, 'modifyUserInfo.html', content)


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
    content['hasNoLikeReviewList'] = (len(likeReviewList) == 0)

    # 좋아요를 누른 제품 목록
    productList = Product.objects.all()
    likeProductList = list()
    for product in productList:
        if user in product.likers.all():
            likeProductList.append(product)
    content['likeProductList'] = likeProductList
    content['hasNoLikeProductList'] = (len(likeProductList) == 0)

    # 작성한 리뷰 목록
    myReviews = PenReview.objects.filter(author=user)
    content['myReviews'] = myReviews
    content['hasMyReviews'] = (len(myReviews) == 0)

    # 웹 판매정보 목록
    if user.is_WebSeller:
        webSellInfoList = WebSellInfo.objects.filter(seller=user)
    else:
        webSellInfoList = []
    content['webSellInfoList'] = webSellInfoList
    content['hasNoWebSellInfoList'] = (len(webSellInfoList) == 0)

    # 문구점 판매정보 목록
    if user.is_Stationer:
        stationerSellInfoList = StationerSellInfo.objects.filter(seller=user)
    else:
        stationerSellInfoList = []
    content['stationerSellInfoList'] = stationerSellInfoList
    content['hasNoStationerSellInfoList'] = (len(stationerSellInfoList) == 0)

    return render(request, 'myPage.html', content)


@login_required(login_url='/account/logIn/')
def myPageRedirector(request, target):
    return redirect(f"/account/myPage#{target}")


def selectSellerType_view(request):
    return render(request, 'selectSellerType.html')


@login_required(login_url='/account/logIn/')
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