from django.contrib import admin
from .models import Product
from .models import WebSellInfo, StationerSellInfo
from .models import PenReview
from .models import ProductTag

admin.site.register(Product)
admin.site.register(WebSellInfo)
admin.site.register(StationerSellInfo)
admin.site.register(PenReview)
admin.site.register(ProductTag)