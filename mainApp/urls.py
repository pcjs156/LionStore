from django.contrib import admin
from django.urls import path

from . import views
from . import tools

# /store/...
urlpatterns = [
    # 프로젝트 메인 페이지
    path('main/', views.mainPage_view, name="mainPage"),

    # 제품 등록 요청 관련
    path('productRequest/', views.productRequest_view, name="productRequestList"),
    path('productRequest/create', views.newProductRequest_view,
         name="newProductRequest"),
    path('productRequest/<int:product_request_id>', views.productRequestDetail_view, name="productRequestDetail"),
    path('productRequest/modify/<int:product_request_id>', views.productRequestModify_view, name="productRequestModify"),
    path('productRequest/delete/<int:product_request_id>', views.productRequestDelete_view, name="productRequestDelete"),

    # 카테고리별 제품 목록
    path('productList/<int:category_id>', views.productList_view, name="productList"),
    # 제품 상세 정보
    path('productDetail/<int:product_id>', views.productDetail_view, name="productDetail"),

    # 제품 좋아요 관련
    path('productLikeProcess/<int:product_id>',
         views.productLikeProcess, name="productLikeProcess"),
    path('productLike/<int:product_id>', views.productLike, name="productLike"),
    path('productDislike/<int:product_id>', views.productDislike, name="productDislike"),

    # 리뷰 관련
    path('productList/<int:product_id>/newReview', views.reviewCreate_view, name="reviewCreate"),
    path('reviewDetail/<int:review_id>', views.reviewDetail_view, name="reviewDetail"),
    path('reviewModify/<int:review_id>', views.reviewModify_view, name="reviewModify"),
    path('reviewUpdate/<int:review_id>', views.reviewUpdate, name="reviewUpdate"),
    path('reviewDelete/<int:review_id>', views.reviewDelete, name="reviewDelete"),
    path('reviewImageModify/<int:review_id>/<path:imageURL>', views.reviewImageModify_view, name="reviewImageModify"),
    path('reviewImageDelete/<int:review_id>/<path:imageURL>', views.reviewImageDelete, name="reviewImageDelete"),
    path('reviewImageAdd/<int:review_id>', views.reviewImageAdd, name="reviewImageAdd"),
     path('firstReviewImageModify/<int:review_id>', views.firstReviewImageModify_view, name="firstReviewImageModify"),
     path('firstReviewImageDelete/<int:review_id>', views.firstReviewImageDelete, name="firstReviewImageDelete"),

     # 댓글 관련
     path('commentCreate/<int:review_id>', views.commentCreate, name="commentCreate"),
     path('commentDelete/<int:comment_id>', views.commentDelete, name="commentDelete"),

    # 리뷰 좋아요
    path('reviewLikeProcess/<int:review_id>',
         views.reviewLikeProcess, name="reviewLikeProcess"),
    path('reviewLike/<int:review_id>', views.reviewLike, name="reviewLike"),
    path('reviewDislike/<int:review_id>', views.reviewDislike, name="reviewDislike"),

    # 웹 판매정보 관련
    path('productList/<int:product_id>/newWebSellInfo', views.webSellInfoCreate_view, name="webSellInfoCreate"),
    path('productList/<int:product_id>/webSellInfoModify/<int:webSellInfo_id>', views.webSellInfoModify_view, name="webSellInfoModify"),
    path('productList/<int:product_id>/webSellInfoDelete/<int:webSellInfo_id>', views.webSellInfoDelete, name="webSellInfoDelete"),

    # 문구점 판매정보 관련
    path('productList/<int:product_id>/newStationerSellInfo', views.stationerSellInfoCreate_view, name="stationerSellInfoCreate"),
    path('productList/<int:product_id>/stationerSellInfoModify/<int:stationerSellInfo_id>', views.stationerSellInfoModify_view, name="stationerSellInfoModify"),
    path('productList/<int:product_id>/stationerSellInfoDelete/<int:stationerSellInfo_id>', views.stationerSellInfoDelete, name="stationerSellInfoDelete"),

    # 검색 관련
    path('searchMain', views.searchMain_view, name="searchMain"),
    path('keywordSearchResult', views.keywordSearchResult_view, name="keywordSearchResult"),
    path('tagSearchResult', views.tagSearchResult_view, name="tagSearchResult"),
    
    # 추천
    path('userRecommendation', views.userRecommendation_view, name="userRecommendation"),

    # 특정 태그가 달려있는 제품의 목록
    path('tagProduct/<int:productTag_id>', views.tagProduct_view, name="tagProduct"),
    # 특정 태그를 가지는 사람들의 리뷰 목록
    path('reviewsByTag/<tagName>', views.reviewsByTag_view, name="reviewsByTag"),

    # 외부 링크로 리다이렉트 하기 위한 url
    path('redirectExternalLink/<path:link>', tools.redirectExternalLink, name='redirectExternalLink'),

     # 카테고리 이름으로 productList에 Redirect
     path('redirectByCategoryName/<categoryName>', tools.redirectByCategoryName, name="redirectByCategoryName"),
]
