from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from.views import custom_password_reset_confirm,custom_password_reset_request, delete_post, HomeView, logout_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # ホーム画面のURLパターン
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:post_id>/delete-ajax/', views.delete_post, name='post_delete_ajax'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('change_password/', views.change_password, name='change_password'),
    path('custom_password_reset/', custom_password_reset_request, name='custom_password_reset_request'),
    path('custom_password_reset/confirm/', custom_password_reset_confirm, name='custom_password_reset_confirm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
