from django.contrib import admin

from .models import *

admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(WebSellInfo)
admin.site.register(StationerSellInfo)
admin.site.register(PenReview)
admin.site.register(ProductTag)
admin.site.register(ProductRequest)