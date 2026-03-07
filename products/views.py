from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category, Review
from .forms import ReviewForm
from django.db.models import Max, Min
def home(request):
    """Главная страница с популярными товарами и категориями"""
    featured_products = Product.objects.filter(in_stock=True).order_by('-created_at')[:8]
    categories = Category.objects.annotate(product_count=Count('product')).filter(product_count__gt=0)[:6]
    
    return render(request, 'products/home.html', {
        'featured_products': featured_products,
        'categories': categories
    })
    
def product_list(request):
    # Получаем параметры фильтрации из GET-запроса
    category_slug = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    in_stock_only = request.GET.get('in_stock', '')
    sort_by = request.GET.get('sort_by', '-created_at')
    
    products = Product.objects.all()
    
    # Фильтрация по категории
    if category_slug != 'all':
        products = products.filter(category__slug=category_slug)
    
    # Фильтрация по поисковому запросу
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Фильтрация по цене
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass  
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass  
    
    # Фильтрация по наличию
    if in_stock_only:
        products = products.filter(in_stock=True)
    
    # Сортировка
    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
        'name_asc': 'name',
        'name_desc': '-name'
    }
    
    sort_field = sort_options.get(sort_by, '-created_at')
    products = products.order_by(sort_field)
    
    categories = Category.objects.annotate(product_count=Count('product')).filter(product_count__gt=0)
    
    paginator = Paginator(products, 12)  # 12 товаров на страницу
    page = request.GET.get('page', 1)
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Получаем минимальную и максимальную цены для фильтра
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Подготавливаем контекст для передачи в шаблон
    context = {
        'products': products_page,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock_only': in_stock_only,
        'sort_by': sort_by,
        'price_range': price_range,
        'filter_params': request.GET.urlencode()  # Для сохранения параметров в пагинации
    }
    
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.filter(is_active=True)
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Отзыв добавлен!')
            return redirect('product_detail', slug=slug)
    else:
        form = ReviewForm()
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })