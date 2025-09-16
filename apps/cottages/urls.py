from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cottages'

router = DefaultRouter()
router.register(r'', views.CottageViewSet)

urlpatterns = [
    path('page/', views.cottages_page.as_view(), name='page'),
    path('debug/', views.CottageDebugView.as_view(), name='debug'),
    path('<int:cottage_id>/', views.CottageDetailView.as_view(), name='detail'),
    path('search/', views.CottageSearchView.as_view(), name='search'),
    path(
        '<int:cottage_id>/availability/',
        views.CottageAvailabilityView.as_view(),
        name='availability'
    ),
    path('', include(router.urls)),
]
