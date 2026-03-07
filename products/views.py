from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Max, Min, Q
from django.shortcuts import get_object_or_404, redirect, render
import base64

from .forms import PlantClassifierForm, ReviewForm
from .huggingface_service import PlantClassifierError, classify_plant_and_recommend
from .models import Category, Product


def home(request):
    """Главная страница с популярными товарами и категориями."""
    featured_products = Product.objects.filter(in_stock=True).order_by('-created_at')[:8]
    categories = Category.objects.annotate(product_count=Count('product')).filter(product_count__gt=0)[:6]

    return render(
        request,
        'products/home.html',
        {
            'featured_products': featured_products,
            'categories': categories,
        },
    )


def plant_classifier(request):
    result = None
    form = PlantClassifierForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        image_file = form.cleaned_data['image']
        try:
            image_bytes = image_file.read()
            result = classify_plant_and_recommend(image_bytes)

            b64_img = base64.b64encode(image_bytes).decode('utf-8')
            content_type = image_file.content_type if hasattr(image_file, 'content_type') else 'image/jpeg'
            result['image_uri'] = f"data:{content_type};base64,{b64_img}"

            messages.success(request, 'Объект успешно распознан!')
        except PlantClassifierError as exc:
            messages.error(request, str(exc))

    return render(
        request,
        'products/plant_classifier.html',
        {
            'form': form,
            'result': result,
        },
    )


def product_list(request):
    category_slug = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    in_stock_only = request.GET.get('in_stock', '')
    sort_by = request.GET.get('sort_by', '-created_at')

    products = Product.objects.all()

    if category_slug != 'all':
        products = products.filter(category__slug=category_slug)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

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

    if in_stock_only:
        products = products.filter(in_stock=True)

    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
        'name_asc': 'name',
        'name_desc': '-name',
    }

    sort_field = sort_options.get(sort_by, '-created_at')
    products = products.order_by(sort_field)

    categories = Category.objects.annotate(product_count=Count('product')).filter(product_count__gt=0)

    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    price_range = products.aggregate(min_price=Min('price'), max_price=Max('price'))

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
        'filter_params': request.GET.urlencode(),
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

    return render(
        request,
        'products/product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'form': form,
        },
    )
