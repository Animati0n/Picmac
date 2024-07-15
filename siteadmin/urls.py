from django.urls import URLPattern, path
from . import views

urlpatterns = [
    path('',views.adminload),
    path('transaction',views.transaction),
    path('newartuploads',views.newArtUpload),
    path('allarts',views.allArts)
]