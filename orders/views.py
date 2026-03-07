from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Order, OrderItem
from .forms import OrderForm
from cart.models import Cart, CartItem
from users.models import UserProfile
import random
import string

def generate_order_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@login_required
def create_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart_view')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = generate_order_number()
            order.total_price = cart.total_price
            
            order.save()
            
            # Переносим товары из корзины в заказ
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Очищаем корзину
            cart.items.all().delete()
            
            messages.success(request, f'Заказ #{order.order_number} успешно создан!')
            return redirect('order_detail', order_id=order.id)
    else:
        # Заполняем форму данными пользователя
        initial_data = {
            'email': request.user.email,
            'phone_number': getattr(profile, 'phone', ''),
            'shipping_address': getattr(profile, 'address', ''),
        }
        form = OrderForm(initial=initial_data)
    
    return render(request, 'orders/create_order.html', {
        'form': form,
        'cart': cart
    })

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Заказ #{order.order_number} отменен')
    else:
        messages.error(request, 'Невозможно отменить заказ в текущем статусе')
    
    return redirect('order_detail', order_id=order.id)

