from django.urls import path
from . import views

urlpatterns = [

    path('addbook/', views.addbook),
    path('viewbooks/', views.viewbooks),
    path('searchbook/', views.searchbook),
    path('addstudent/', views.addstudent),
    path('viewstudents/', views.viewstudents),
    path('issuebook/', views.issuebook),
    path('returnbook/', views.returnbook),
    path('trackbooks/', views.trackbooks),
    path('login/', views.login),
]
