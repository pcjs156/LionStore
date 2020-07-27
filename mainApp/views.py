from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def introPage_view(request):
    return render(request, 'introPage.html')

def mainPage_view(request):
    if request.user.is_authenticated:
        print(request.user.is_Customer)
        print(request.user.is_WebSeller)
        print(request.user.is_Stationer)

    return render(request, 'mainPage.html')