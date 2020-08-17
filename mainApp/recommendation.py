from .models import *
from account.models import *

from math import sqrt

def cos_similarity(user1:Customer, user2:Customer):
    user1_reviews = PenReview.objects.filter(author=user1)
    user2_reviews = PenReview.objects.filter(author=user2)
    
    productIntersection = set()
    for review1 in user1_reviews:
        for review2 in user2_reviews:
            if review1.product == review2.product:
                productIntersection.add(review1.product)

    # 누구와도 같은 제품을 리뷰한 적이 없는 경우
    if len(productIntersection) == 0:
        return -1
    
    ret = float((sum([user1_reviews.get(product=product).totalScore+1 for product in productIntersection]))) * \
        float((sum([user1_reviews.get(product=product).totalScore+1 for product in productIntersection])))

    ret /= sqrt(sum([user1_reviews.get(product=product).totalScore+1 for product in productIntersection]))
    ret /= sqrt(sum([user2_reviews.get(product=product).totalScore+1 for product in productIntersection]))

    return ret

# 범위 : 0 ~ 5
def orderby_similarity(targetUser : Customer, maxNum=5):
    users = Customer.objects.exclude(username=targetUser.username)
    similarityPair = [[user, cos_similarity(targetUser, user)] for user in users]
    similarityPair.sort(key=lambda p: p[1], reverse=True)
    similarityPair = list(filter(lambda p: p[1] != -1, similarityPair))
    similarityPair = list(map(lambda p: (p[0], p[1]-1), similarityPair))

    return similarityPair[:maxNum]