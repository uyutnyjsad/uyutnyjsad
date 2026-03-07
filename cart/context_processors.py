def cart(request):
    if request.user.is_authenticated:
        # Используем 'profile' вместо 'userprofile'
        cart, created = request.user.cart_set.get_or_create()
        # Добавляем безопасные URL для изображений товаров в корзине
        for item in cart.items.all():
            if hasattr(item.product, 'image_url'):
                item.product.safe_image_url = item.product.image_url
            else:
                item.product.safe_image_url = '/static/images/product-placeholder.jpg'
        return {'cart': cart}
    return {'cart': None}