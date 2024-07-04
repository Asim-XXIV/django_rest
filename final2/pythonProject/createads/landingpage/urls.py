from django.urls import path
from .views import AdminAdvertisementCreateView

urlpatterns = [
    path('admin-ads/', AdminAdvertisementCreateView.as_view(), name='Admin_Advertisement'),

]
