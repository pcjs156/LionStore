from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Product, ProductCategory, PenReview, Score

from .forms import PenReviewForm

def intro_view(request):
    return render(request, 'intro.html')

def mainPage_view(request):
    return render(request, 'main.html')

def newProductRequest_view(request):
    return render(request, 'newProductRequest.html')

def productDetail_view(request, category_id, prodict_id):
    return render(request, 'productDetail.html')

def productList_view(request, category_id):
    return render(request, 'productList.html')

def productRequest_view(request):
    return render(request, 'productRequest.html')

def productRequestDetail_view(request, product_request_id):
    return render(request, 'productRequestDetail.html')

def newProductRequestDetail_view(request, product_request_id):
    return render(request, 'newProductRequestDetail.html')

def productRequestModify_view(request, product_request_id):
    return render(request, 'productRequestModify.html')

def rateBackUp_view(request):
    return render(request, 'rateBackUp.html')

def reviewCreate_view(request, product_id):
    return render(request, 'reviewCreate.html')

def reviewDetail_view(request, product_id, review_id):
    return render(request, 'reviewDetail.html')

def reviewModify_view(request, product_id, review_id):
    return render(request, 'reviewModify.html')

def searchMain_view(request):
    return render(request, 'searchMain.html')

def searchResult_view(request):
    return render(request, 'searchResult.html')

def stationerSellInfoCreate_view(request, category_id, product_id):
    return render(request, 'stationerSellInfoCreate.html')

def stationerSellInfoDetail_view(request, category_id, product_id, stationerSellInfo_id):
    return render(request, 'stationerSellInfoDetail.html')

def stationerSellInfoModify_view(request, category_id, product_id, stationerSellInfo_id):
    return render(request, 'stationerSellInfoModify.html')

def webSellInfoCreate_view(request, category_id, product_id):
    return render(request, 'webSellInfoCreate.html')

def webSellInfoDetail_view(request, category_id, product_id, webSellInfo_id):
    return render(request, 'webSellInfoDetail.html')

def webSellInfoModify_view(request, category_id, product_id, webSellInfo_id):
    return render(request, 'webSellInfoModify.html')


# 이하 테스트용(삭제 예정) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


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