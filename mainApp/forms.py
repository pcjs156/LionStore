from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import PenReview
from .widgets import starWidget

class PenReviewForm(forms.ModelForm):
    class Meta:
        model = PenReview
        fields = ['goodPoint', 'weakPoint', 'rawTagString',
        'reviewImage1', 'reviewImage2', 'reviewImage3', 'reviewImage4', 'reviewImage5', 'reviewImage6',]

        # widgets = {
        #     'totalScore' : starWidget,
        #     'grip' : starWidget,
        #     'life' : starWidget,
        #     'durability' : starWidget,
        #     'design' : starWidget,
        #     'texture' : starWidget,
        #     'costEffetiveness' : starWidget,
        #     'versatility' : starWidget,
        # }