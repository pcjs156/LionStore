from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.mainPage_view, name="mainPage"),
    path('categoryList/', views.categoryListTest_view, name="categoryList"),
    path('categoryList/<int:category_id>', views.productListTest_view, name="productList"),
    path('newReview/<int:product_id>', views.newReviewTest_view, name="newReiewTest"),

]
