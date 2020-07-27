from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import UserSignUpForm, UserLoginForm

from django.contrib.auth import login, authenticate, logout

def selectCustomerType_view(request):
    return render(request, 'selectCustomerType.html')

def userSignUp_view(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.save()

            login(request, user)
            return redirect("mainPage")
        
        return render(request, 'userSignUpPage.html', {'form':form})


    else :
        form = UserSignUpForm()
        return render(request, 'userSignUpPage.html', {'form':form})


def webSellerSignUp_view(request):
    return render(request, 'webSellerSignUpPage.html')

def stationerSignUp_view(request):
    return render(request, 'stationerSignUpPage.html')

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST )
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