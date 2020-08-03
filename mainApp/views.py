from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Product, ProductCategory, PenReview, Score

from .forms import PenReviewForm

def introPage_view(request):
    return render(request, 'introPage.html')

def mainPage_view(request):
    if request.user.is_authenticated:
        print(f"{request.user}님께서 접속하셨습니다.")

    return render(request, 'newReviewTest.html')

def categoryListTest_view(request):
    categoryList = ProductCategory.objects.all()

    return render(request, 'categoryListTest.html', {'categoryList':categoryList})

def productListTest_view(request, category_id):
    category = ProductCategory.objects.get(pk=category_id)
    products = Product.objects.filter(category=category)

    return render(request, 'productListTest.html', {'products':products})


def newReviewTest_view(request, product_id):
    if request.method == 'POST':
        form = PenReviewForm(request.POST)

        product = Product.objects.get(pk=product_id)
        new_review = PenReview(product=product)
        new_review.author = request.user
        new_review.pub_date = timezone.now()
        new_review.goodPoint = request.POST['goodPoint']
        new_review.weakPoint = request.POST['weakPoint']
        new_review.save()

        new_review.totalScore = Score.objects.create(review=new_review, name="총점", score=int(request.POST['totalScore']))
        new_review.grip = Score.objects.create(review=new_review, name="그립감", score=int(request.POST['grip']))
        new_review.life = Score.objects.create(review=new_review, name="제품 수명", score=int(request.POST['life']))
        new_review.durability = Score.objects.create(review=new_review, name="내구도", score=int(request.POST['durability']))
        new_review.design = Score.objects.create(review=new_review, name="디자인", score=int(request.POST['design']))
        new_review.texture = Score.objects.create(review=new_review, name="사용감", score=int(request.POST['texture']))
        new_review.costEffetiveness = Score.objects.create(review=new_review, name="가성비", score=int(request.POST['costEffetiveness']))
        new_review.versatility = Score.objects.create(review=new_review, name="범용성", score=int(request.POST['versatility']))

        new_review.save()
        return redirect('mainPage')

    else :
        form = PenReviewForm()
        return render(request, 'newReviewTest.html', {'form':form})

def newMapTest_view(request):
    if request.method == "POST":
        print(request.POST["stationerStoreLocation"])

    return render(request, 'mapTest.html')


def newMapResult_view(request):
    return render(request, 'mapTestResult.html')