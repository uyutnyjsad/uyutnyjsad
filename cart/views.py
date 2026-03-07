from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from products.models import Product

def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request.user)
    
    # Определяем количество из POST или используем 1 по умолчанию
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
    else:
        quantity = 1  # Для GET запросов используем 1
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product
    )
    
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
        
    cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.items.count(),
            'message': f'Товар {product.name} добавлен в корзину'
        })
    
    messages.success(request, f'Товар {product.name} добавлен в корзину')
    
    # Перенаправляем на предыдущую страницу или на список товаров
    redirect_url = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(redirect_url)

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количество обновлено')
        else:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины')
    
    return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('cart_view')

@login_required
def clear_cart(request):
    cart = get_or_create_cart(request.user)
    cart.items.all().delete()
    messages.success(request, 'Корзина очищена')
    return redirect('cart_view')