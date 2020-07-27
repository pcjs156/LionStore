from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import UserSignUpForm, UserLoginForm, WebSellerSignUpForm, StationerSignUpForm

from django.contrib.auth import login, authenticate, logout

@login_required
def accountMain_view(request):
    return render(request, 'accountMain.html')

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
    if request.method == 'POST':
        form = WebSellerSignUpForm(request.POST)

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
        form = StationerSignUpForm(request.POST)

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