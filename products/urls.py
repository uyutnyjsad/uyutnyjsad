from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<slug:slug>/', views.product_detail, name='product_detail'),
    path('ai/plant-classifier/', views.plant_classifier, name='plant_classifier'),
]
