from django.urls import path

from artist.views import payment
from . import views

urlpatterns = [
    path('',views.home),
    path('/booknow',views.bookNow),
    path('/payment',views.payment),
    path('/quickView',views.quickView),
    path('/myorders',views.myorders),
    path('/requestnow',views.requestNow),
    path('/myrequests',views.myrequests),
    path('/searchResult',views.searchResult),
    
]