from faker import Faker
import random

CATEGORY_NAMES = tuple("볼펜 만년필 캘리그라피펜 연필 색연필 형광펜 샤프펜슬 유성펜 사인펜 젤펜 기타".split(' '))

from mainApp.models import Product, ProductCategory

def initializeCategory():
    # 카테고리 리스트가 비었을 때만 사용하기
    if len(ProductCategory.objects.all()) != 0:
        print("@@@@@ 카테고리 초기화를 진행하지 않습니다.")
        print("@@@@@ 카테고리가 없을 때만 사용할 수 있습니다.")
        return
    
    for name in CATEGORY_NAMES:
        ProductCategory.objects.create(categoryName=name)

def automativeFilling_Product(countLimit=10):
    fakerInstance = Faker()

    productList = Product.objects.all()

    if len(productList) > countLimit:
        print(f"이미 {countLimit}개의 Product 모델이 존재해 새로 모델을 생성하지 않습니다.")
        return

    categories = ProductCategory.objects.all()
    for i in range(countLimit - len(productList)):
        Product.objects.create(category=random.choice(categories), manufacturer=fakerInstance.name(), description=fakerInstance.text(), name=fakerInstance.name())

def getHash(rawLink):
    return rawLink.split('=')[1]