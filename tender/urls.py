from django.urls import path
from .views import Tender

urlpatterns = [
    path('', Tender.as_view())
]
