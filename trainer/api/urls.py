from rest_framework.routers import DefaultRouter

from trainer.api import views


router = DefaultRouter()
router.register(r'cards', views.CardViewSet)
router.register(r'dictionary-cards', views.DictionaryCardViewSet)
router.register(r'my-dictionary', views.MyDictionaryViewSet)

urlpatterns = router.urls