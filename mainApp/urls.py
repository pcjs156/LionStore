from django.contrib import admin
from django.urls import path

from . import views

# /store/...
urlpatterns = [
    # 프로젝트 메인 페이지
    path('main/', views.mainPage_view, name="mainPage"),

    # 제품 등록 요청 관련
    path('productRequest/', views.productRequest_view, name="productRequestList"),
    path('productRequest/create', views.newProductRequest_view, name="newProductRequest"),
    path('productRequest/<int:product_request_id>', views.productRequestDetail_view, name="productRequestDetail"),
    path('productRequest/modify/<int:product_request_id>', views.productRequestModify_view, name="productRequestModify"),

    # 카테고리별 제품 목록
    path('productList/<int:category_id>', views.productList_view, name="productList"),
    # 제품 상세 정보
    path('productList/<int:category_id>/<int:product_id>', views.productDetail_view, name="productDetail"),

    # 리뷰 관련
    path('productList/<int:category_id>/<int:product_id>/newReview', views.reviewCreate_view, name="reviewCreate"),
    path('productList/<int:category_id>/<int:product_id>/reviewDetail/<int:review_id>', views.reviewDetail_view, name="reviewDetail"),
    path('productList/<int:category_id>/<int:product_id>/reviewModify/<int:review_id>', views.reviewModify_view, name="reviewModify"),

    # 웹 판매정보 관련
    path('productList/<int:category_id>/<int:product_id>/newWebSellInfo', views.webSellInfoCreate_view, name="webSellInfoCreate"),
    path('productList/<int:category_id>/<int:product_id>/webSellInfoDetail/<int:webSellInfo_id>', views.webSellInfoDetail_view, name="webSellInfoDetail"),
    path('productList/<int:category_id>/<int:product_id>/webSellInfoModify/<int:webSellInfo_id>', views.webSellInfoModify_view, name="webSellInfoModify"),

    # 문구점 판매정보 관련
    path('productList/<int:category_id>/<int:product_id>/newReview', views.stationerSellInfoCreate_view, name="stationerSellInfoCreate"),
    path('productList/<int:category_id>/<int:product_id>/stationerSellInfoDetail/<int:stationerSellInfo_id>', views.stationerSellInfoDetail_view, name="stationerSellInfoDetail"),
    path('productList/<int:category_id>/<int:product_id>/stationerSellInfoModify/<int:stationerSellInfo_id>', views.stationerSellInfoModify_view, name="stationerSellInfoModify"),

    # 검색 관련
    path('searchMain', views.searchMain_view, name="searchMain"),
    path('searchResult', views.searchResult_view, name="searchResult"),
    

    # 테스트용
    path('categoryList/', views.categoryListTest_view, name="categoryList"),
    path('newReview/<int:product_id>', views.newReviewTest_view, name="newReiewTest"),
    path('newMapTest', views.newMapTest_view, name="newMapTest"),
]
