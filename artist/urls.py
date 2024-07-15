from django.urls import path
from . import views

urlpatterns = [
    path('artistdash/profile',views.profile),
    path('artistdash/store',views.artuploads),
    path('artistdash/earnings',views.earnings),
    path('artistdash/subscription',views.subscriptiondetails),
    path('artistdash/requests',views.artrequest),
    path('artistdash/subscription/page',views.subscription),
    #path('artistdash/edit',views.edit),
    path('payment',views.payment)
    
]

