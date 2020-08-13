from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import PenReview
from .models import ProductRequest
from .widgets import starWidget

class PenReviewForm(forms.ModelForm):
    class Meta:
        model = PenReview
        fields = ['goodPoint', 'weakPoint', 'rawTagString',
        'reviewImage1', 'reviewImage2', 'reviewImage3', 'reviewImage4', 'reviewImage5', 'reviewImage6',]


class ReviewImageModifyingForm(forms.ModelForm):
    class Meta:
        model = PenReview
        fields = ['reviewImage1']


class NewProductRequestForm(forms.ModelForm):
    class Meta:
        model = ProductRequest
        fields = ['productName', 'productBrand', 'productDescription',]