from django.contrib import admin
from django.urls import path, include

import mainApp.views

import account.urls
import mainApp.urls

urlpatterns = [
    path('', mainApp.views.introPage_view, name='introPage'),
    path('admin/', admin.site.urls),
    path('account/', include(account.urls)),
    path('store/', include(mainApp.urls)),
]
