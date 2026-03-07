from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category, Review
from orders.models import Order, OrderItem
from users.models import UserProfile
from django.contrib.auth.models import User
from .forms import ProductAdminForm, CategoryAdminForm, OrderAdminForm, UserAdminForm
from django.core.paginator import Paginator

def staff_required(function):
    decorator = user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')
    return decorator(function)

@staff_required
def dashboard(request):
    # Статистика
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Правильный расчет выручки (только завершенные заказы)
    completed_orders = Order.objects.filter(status='delivered')
    total_revenue = completed_orders.aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    stats = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_orders': Order.objects.count(),
        'total_users': User.objects.count(),
        'total_reviews': Review.objects.count(),
        
        'recent_orders': Order.objects.filter(created_at__date=today).count(),
        'weekly_orders': Order.objects.filter(created_at__gte=week_ago).count(),
        'monthly_orders': Order.objects.filter(created_at__gte=month_ago).count(),
        
        'total_revenue': total_revenue,
        'pending_orders': Order.objects.filter(status='pending').count(),
        'completed_orders': completed_orders.count(),
    }
    
    # Последние заказы
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    # Популярные товары
    popular_products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]
    
    # Статусы заказов для графика
    order_statuses = Order.objects.values('status').annotate(count=Count('id'))
    
    return render(request, 'dashboard/dashboard.html', {
        'stats': stats,
        'recent_orders': recent_orders,
        'popular_products': popular_products,
        'order_statuses': order_statuses,
    })

# CRUD для товаров
@staff_required
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    
    # Поиск и фильтрация
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    return render(request, 'dashboard/products/list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    })

@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Товар "{product.name}" успешно создан!')
            return redirect('dashboard:product_list')
    else:
        form = ProductAdminForm()
    
    return render(request, 'dashboard/products/form.html', {
        'form': form,
        'title': 'Создать товар'
    })

@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Товар "{product.name}" успешно обновлен!')
            return redirect('dashboard:product_list')
    else:
        form = ProductAdminForm(instance=product)
    
    return render(request, 'dashboard/products/form.html', {
        'form': form,
        'title': 'Редактировать товар',
        'product': product
    })

@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Товар "{product_name}" успешно удален!')
        return redirect('dashboard:product_list')
    
    return render(request, 'dashboard/products/delete.html', {
        'product': product
    })

# CRUD для категорий
@staff_required
def category_list(request):
    categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('name')
    
    return render(request, 'dashboard/categories/list.html', {
        'categories': categories
    })

@staff_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryAdminForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория "{category.name}" успешно создана!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryAdminForm()
    
    return render(request, 'dashboard/categories/form.html', {
        'form': form,
        'title': 'Создать категорию'
    })

@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryAdminForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория "{category.name}" успешно обновлена!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryAdminForm(instance=category)
    
    return render(request, 'dashboard/categories/form.html', {
        'form': form,
        'title': 'Редактировать категорию',
        'category': category
    })

@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Категория "{category_name}" успешно удалена!')
        return redirect('dashboard:category_list')
    
    return render(request, 'dashboard/categories/delete.html', {
        'category': category
    })

# CRUD для заказов
@staff_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/orders/list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES
    })

@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        form = OrderAdminForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Заказ #{order.order_number} успешно обновлен!')
            return redirect('dashboard:order_detail', pk=order.pk)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = OrderAdminForm(instance=order)
    
    return render(request, 'dashboard/orders/detail.html', {
        'order': order,
        'form': form
    })

@staff_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        order_number = order.order_number
        order.delete()
        messages.success(request, f'Заказ #{order_number} успешно удален!')
        return redirect('dashboard:order_list')
    
    return render(request, 'dashboard/orders/delete.html', {
        'order': order
    })

# CRUD для пользователей
@staff_required
def user_list(request):
    # Используем 'profile' вместо 'userprofile'
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) | 
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query)
        )
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Обновляем обращение к профилю
    for user in page_obj:
        if hasattr(user, 'profile') and user.profile.avatar:
            user.avatar_url = user.profile.avatar_url
        else:
            user.avatar_url = '/static/images/avatar-placeholder.jpg'
    
    return render(request, 'dashboard/users/list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@staff_required
def user_detail(request, pk):
    # Исправляем 'userprofile' на 'profile'
    user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    user_orders = Order.objects.filter(user=user).order_by('-created_at')
    user_reviews = Review.objects.filter(user=user).order_by('-created_at')
    if hasattr(user, 'profile') and user.profile.avatar:
        user.avatar_url = user.profile.avatar_url
    else:
        user.avatar_url = '/static/images/avatar-placeholder.jpg'
    if request.method == 'POST':
        form = UserAdminForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Пользователь {user.username} успешно обновлен!')
            return redirect('dashboard:user_list')
    else:
        form = UserAdminForm(instance=user)
    
    return render(request, 'dashboard/users/detail.html', {
        'user': user,
        'form': form,
        'user_orders': user_orders[:5],
        'user_reviews': user_reviews[:5],
        'total_orders': user_orders.count(),
        'total_reviews': user_reviews.count()
    })

# Управление отзывами
@staff_required
def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        reviews = reviews.filter(is_active=True)
    elif status_filter == 'inactive':
        reviews = reviews.filter(is_active=False)
    
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboard/reviews/list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter
    })

@staff_required
def review_toggle(request, pk):
    review = get_object_or_404(Review, pk=pk)
    
    if review.is_active:
        review.is_active = False
        messages.success(request, 'Отзыв скрыт')
    else:
        review.is_active = True
        messages.success(request, 'Отзыв активирован')
    
    review.save()
    return redirect('dashboard:review_list')

@staff_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв успешно удален!')
        return redirect('dashboard:review_list')
    
    return render(request, 'dashboard/reviews/delete.html', {
        'review': review
    })