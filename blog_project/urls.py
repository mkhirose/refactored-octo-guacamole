from django.contrib import admin
from django.urls import path
from django.urls import path, include  # includeを追加

urlpatterns = [
    path('admin/', admin.site.urls),
]
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),  # ここで blog.urls をインクルードしているか確認
]
