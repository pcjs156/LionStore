from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import mainApp.views

import account.urls
import mainApp.urls

urlpatterns = [
    path('', mainApp.views.intro_view, name='introPage'),
    path('admin/', admin.site.urls),
    path('account/', include(account.urls)),
    path('store/', include(mainApp.urls)),
    path('randomLike/', mainApp.views.randomLike, name="randomLike"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
