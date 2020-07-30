from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def introPage_view(request):
    return render(request, 'introPage.html')

def mainPage_view(request):
    if request.user.is_authenticated:
        print(f"{request.user}님께서 접속하셨습니다.")

    return render(request, 'mainPage.html')