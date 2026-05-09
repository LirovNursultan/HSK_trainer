from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from trainer.auth_views import register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/', include('trainer.api.urls')),

    # JWT авторизация
    path('api/auth/login/',    TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/',  TokenRefreshView.as_view(),    name='token_refresh'),
    path('api/auth/register/', register,                      name='register'),

    # Обычные страницы
    path('', include('trainer.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)