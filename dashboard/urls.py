from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Главная страница дашборда
    path('', views.dashboard, name='dashboard'),
    
    # Товары
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Категории
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Заказы
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    
    # Пользователи
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    
    # Отзывы
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:pk>/toggle/', views.review_toggle, name='review_toggle'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
]