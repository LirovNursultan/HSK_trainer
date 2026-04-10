from rest_framework.routers import DefaultRouter
from .views import CardViewSet, MyDictionaryViewSet

router = DefaultRouter()

router.register(r'cards', CardViewSet, basename='cards')
router.register(r'my-dictionary', MyDictionaryViewSet, basename='my-dictionary')

urlpatterns = router.urls