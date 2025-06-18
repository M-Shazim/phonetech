# main/context_processors.py

from .models import CartItem

def cart_item_count(request):
    count = 0
    if request.user.is_authenticated:
        count = CartItem.objects.filter(cart__user=request.user).count()
    return {'cart_count': count}

from .models import Cart, CartItem

def cart_count_processor(request):
    count = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = sum(item.quantity for item in CartItem.objects.filter(cart=cart))
        except Cart.DoesNotExist:
            count = 0
    else:
        cart = request.session.get('cart', {})
        count = sum(cart.values())

    return {'cart_count': count}

