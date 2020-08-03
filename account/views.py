from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import UserSignUpForm, UserLoginForm, WebSellerSignUpForm, StationerSignUpForm

from account.models import Customer, CustomerTag

from django.contrib.auth import login, authenticate, logout

def selectCustomerType_view(request):
    return render(request, 'selectCustomerType.html')

def connectTagToUser(user:Customer, rawString:str):
    # 일반 str문자열 : 띄어쓰기를 기준으로 태그 정보가 나누어져 있음
    rawTags = rawString.split(' ')
    # 현재 존재하는 태그의 목록
    existTags = CustomerTag.objects.all()
    
    # 새로 만들어질 태그가 이미 존재한다면 새로 생성하지 않는다.
    for newTagName in rawTags:
        alreadyExists = False
        for existTag in existTags:
            if existTag.__str__() == newTagName:
                alreadyExists = True
                break
        
        if not alreadyExists:
            print(newTagName + " 태그가 존재하지 않아 새로 생성합니다.")
            newTag = CustomerTag.objects.create(tagBody=newTagName)
            user.tags.add(newTag)
        else:
            existTag = CustomerTag.objects.get(tagBody=newTagName)
            user.tags.add(existTag)

        newTag.targetCustomer.add(user)

def userSignUp_view(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            user.save()
            connectTagToUser(user, form.cleaned_data['rawTagString'])

            login(request, user)
            return redirect("mainPage")
        
        return render(request, 'userSignUpPage.html', {'form':form})


    else :
        form = UserSignUpForm()
        return render(request, 'userSignUpPage.html', {'form':form})

def webSellerSignUp_view(request):
    if request.method == 'POST':
        form = WebSellerSignUpForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            user.save()

            login(request, user)
            return redirect("mainPage")
        
        return render(request, 'webSellerSignUpPage.html', {'form':form})

    else :
        form = WebSellerSignUpForm()
        return render(request, 'webSellerSignUpPage.html', {'form':form})


def stationerSignUp_view(request):
    if request.method == 'POST':
        form = StationerSignUpForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            user.save()

            login(request, user)
            return redirect("mainPage")
        
        return render(request, 'stationerSignUpPage.html', {'form':form})

    else :
        form = StationerSignUpForm()
        return render(request, 'stationerSignUpPage.html', {'form':form})


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

            return render(request, 'logInPage.html', {'form':form})
            

    else :
        form = UserLoginForm()
        return render(request, 'logInPage.html', {'form':form})


def logout_view(request):
    logout(request)
    return redirect("mainPage")

def accountInfo_view(request):
    return render(request, 'accountInfo.html')

def interests_view(request):
    return render(request, 'interests.html')

def likeReviews_view(request):
    return render(request, 'likeReviews.html')

def modifyStationerSellInfo_view(request):
    return render(request, 'modifyStationerSellInfo.html')

def modifyUserInfo_view(request):
    return render(request, 'modifyUserInfo.html')

def modifyWebSellerInfo_view(request):
    return render(request, 'modifyWebSellerInfo.html')

def reviewList_view(request):
    return render(request, 'reviewList.html')

def selectSellerType_view(request):
    return render(request, 'selectSellerType.html')

def stationerSellInfoList_view(request):
    return render(request, 'stationerSellInfoList.html')

def webSellerInfoList_view(request):
    return render(request, 'webSellerInfoList.html')