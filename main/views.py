from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, CartItem, Cart,  Review 
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from urllib.parse import quote

def clear_whatsapp_session(request):
    if 'whatsapp_link' in request.session:
        del request.session['whatsapp_link']
    return HttpResponse("Session cleared")




# Home page with special products and banner

def privacy_policy_view(request):
    return render(request, 'privacy_policy.html')

def faq_view(request):
    return render(request, 'faq.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # Merge session cart to DB cart
            session_cart = request.session.get('cart', {})
            for key, quantity in session_cart.items():
                try:
                    product_id, color_id = key.split('_')
                    product = get_object_or_404(Product, id=int(product_id))
                    color = get_object_or_404(Color, id=int(color_id))

                    # Get or create the user's cart
                    cart, _ = Cart.objects.get_or_create(user=user)

                    # Then attach items to that cart
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart, product=product, color=color,
                        defaults={'quantity': quantity}
                    )
                    if not created:
                        cart_item.quantity += quantity
                        cart_item.save()
                except ValueError:
                    continue  # skip invalid keys


            # Clear session cart
            request.session['cart'] = {}

            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})



def add_review(request, id):
    product = get_object_or_404(Product, id=id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        username = request.POST.get('username', '').strip()

        if request.user.is_authenticated:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
        else:
            Review.objects.create(
                product=product,
                username=username or "Anonymous",
                rating=rating,
                comment=comment
            )

    return redirect('product_detail', id=id)  # adjust as needed

@login_required
def account_view(request):
    return render(request, 'account.html', {'user': request.user})

def search_view(request):
    query = request.GET.get('q')
    products = Product.objects.filter(title__icontains=query) if query else []
    return render(request, 'search_results.html', {'query': query, 'products': products})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def home_view(request):
# Fetch all products
    products = Product.objects.all()
    # Fetch special products (your existing logic)
    special_products = Product.objects.filter(is_special=True)  # Adjust based on your model
    # Get category choices from Product model
    product_categories = Product.CATEGORY_CHOICES

    context = {
        'products': products,
        'special_products': special_products,
        'product_categories': product_categories,
    }
    return render(request, 'home.html', context)

# Product listing page
def product_list_view(request):
    selected_categories = request.GET.getlist('category')
    products = Product.objects.all()

    if selected_categories:
        products = products.filter(category__in=selected_categories)

    context = {
        'products': products,
        'selected_categories': selected_categories,
    }
    return render(request, 'product_list.html', {'products': products})

# Product detail page
def product_detail_view(request, id):
    product = get_object_or_404(Product, id=id)
    print("DESC FROM DB:", repr(product.description))  # This will show if whitespace or special chars exist
    return render(request, 'product_detail.html', {'product': product})



# Add to cart logic
from .models import CartItem, Color # if not already

def add_to_cart_view(request, id):
    product = get_object_or_404(Product, id=id)
    quantity = int(request.POST.get('quantity', 1))
    color_id = request.POST.get('color')
    if color_id:
        color = get_object_or_404(Color, id=color_id)
    else:
        color = product.colors.first()  # Pick the first available color
        if not color:
            messages.error(request, "No color option available for this product.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Try to find existing item with same color
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            color=color,  # <- match by color too
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
    else:
        cart = request.session.get('cart', {})
        key = f"{id}_{color.id}"
        cart[key] = cart.get(key, 0) + quantity
        request.session['cart'] = cart

    messages.success(request, f"Added {product.title} ({color.name if color else ''}) to cart.")
    return redirect('cart')



# def add_to_cart_view(request, id):
#     product = get_object_or_404(Product, id=id)
#     quantity = int(request.POST.get('quantity', 1))

#     if request.user.is_authenticated:
#         # Get or create a cart for the user
#         cart, created = Cart.objects.get_or_create(user=request.user)

#         # Check if item already exists in the cart
#         cart_item, created = CartItem.objects.get_or_create(
#             cart=cart, product=product,
#             defaults={'quantity': quantity}
#         )
#         if not created:
#             cart_item.quantity += quantity
#             cart_item.save()
#     else:
#         # Guest user session-based cart
#         cart = request.session.get('cart', {})
#         if str(id) in cart:
#             cart[str(id)] += quantity
#         else:
#             cart[str(id)] = quantity
#         request.session['cart'] = cart

#     messages.success(request, f"Added {product.title} to cart.")
#     return redirect('cart')



# Cart view
def cart_view(request):
    cart_items = []
    total = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_items_queryset = CartItem.objects.select_related('color').filter(cart=cart)
            for item in cart_items_queryset:
                subtotal = item.product.price * item.quantity
                total += subtotal
                cart_items.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'color': item.color,  # include color
                    'subtotal': subtotal
                })
    else:
        session_cart = request.session.get('cart', {})
        for key, quantity in session_cart.items():
            try:
                product_id, color_id = key.split('_')
                product = get_object_or_404(Product, id=product_id)
                color = get_object_or_404(Color, id=color_id)
                subtotal = product.price * quantity
                total += subtotal
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'color': color,
                    'subtotal': subtotal
                })
            except ValueError:
                continue  # fallback in case old keys exist

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

# def cart_view(request):
#     cart_items = []
#     total = 0

#     if request.user.is_authenticated:
#         cart = Cart.objects.filter(user=request.user).first()
#         if cart:
#             cart_items_queryset = CartItem.objects.filter(cart=cart)
#             for item in cart_items_queryset:
#                 subtotal = item.product.price * item.quantity
#                 total += subtotal
#                 cart_items.append({
#                     'product': item.product,
#                     'quantity': item.quantity,
#                     'subtotal': subtotal
#                 })
#     else:
#         session_cart = request.session.get('cart', {})
#         for product_id, quantity in session_cart.items():
#             product = get_object_or_404(Product, id=product_id)
#             subtotal = product.price * quantity
#             total += subtotal
#             cart_items.append({
#                 'product': product,
#                 'quantity': quantity,
#                 'subtotal': subtotal
#             })

#     return render(request, 'cart.html', {
#         'cart_items': cart_items,
#         'total': total
#     })


@require_POST
@require_POST
def update_cart(request, product_id):
    color_id = request.POST.get('color_id')

    action = request.POST.get('action')

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return redirect('cart')

        cart_item = CartItem.objects.filter(cart=cart, product_id=product_id, color_id=color_id).first()
        if not cart_item:
            return redirect('cart')

        if action == 'increase' and cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()

    else:
        key = f"{product_id}_{color_id}"
        cart = request.session.get('cart', {})
        current_qty = cart.get(key, 0)
        product = get_object_or_404(Product, id=product_id)

        if action == 'increase' and current_qty < product.stock:
            cart[key] = current_qty + 1
        elif action == 'decrease' and current_qty > 1:
            cart[key] = current_qty - 1
        request.session['cart'] = cart

    return redirect('cart')

# def update_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     action = request.POST.get('action')

#     if request.user.is_authenticated:
#         cart = Cart.objects.filter(user=request.user).first()
#         if not cart:
#             return redirect('cart')

#         cart_item = CartItem.objects.filter(cart=cart, product=product).first()
#         if not cart_item:
#             return redirect('cart')

#         if action == 'increase' and cart_item.quantity < product.stock:
#             cart_item.quantity += 1
#             cart_item.save()
#         elif action == 'decrease' and cart_item.quantity > 1:
#             cart_item.quantity -= 1
#             cart_item.save()

#     else:
#         cart = request.session.get('cart', {})
#         current_qty = cart.get(str(product_id), 0)
#         if action == 'increase' and current_qty < product.stock:
#             cart[str(product_id)] = current_qty + 1
#         elif action == 'decrease' and current_qty > 1:
#             cart[str(product_id)] = current_qty - 1
#         request.session['cart'] = cart

#     return redirect('cart')

@require_POST
def remove_from_cart(request, product_id):
    color_id = request.POST.get('color_id')


    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart, product_id=product_id, color_id=color_id).delete()
    else:
        key = f"{product_id}_{color_id}"
        cart = request.session.get('cart', {})
        cart.pop(key, None)
        request.session['cart'] = cart

    return redirect('cart')
# def remove_from_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     if request.user.is_authenticated:
#         cart = Cart.objects.filter(user=request.user).first()
#         if cart:
#             CartItem.objects.filter(cart=cart, product=product).delete()
#     else:
#         cart = request.session.get('cart', {})
#         cart.pop(str(product_id), None)
#         request.session['cart'] = cart

#     return redirect('cart')

# Checkout view
def checkout_view(request):
    cart_items = []
    total = 0

    if request.user.is_authenticated:
        cart_items_db = CartItem.objects.select_related('color').filter(cart__user=request.user)
        for item in cart_items_db:
            subtotal = item.product.price * item.quantity
            total += subtotal
            cart_items.append({
                'product': item.product,
                'quantity': item.quantity,
                'color': item.color,
                'subtotal': subtotal,
            })
    else:
        cart = request.session.get('cart', {})
        for key, quantity in cart.items():
            try:
                product_id, color_id = key.split('_')
                product = Product.objects.get(id=product_id)
                color = Color.objects.get(id=color_id)
                subtotal = product.price * quantity
                total += subtotal
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'color': color,
                    'subtotal': subtotal,
                })
            except ValueError:
                continue

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

# def checkout_view(request):
#     cart_items = []
#     total = 0

#     if request.user.is_authenticated:
#         # Use DB cart for logged-in users
#         cart_items_db = CartItem.objects.filter(cart__user=request.user)
#         for item in cart_items_db:
#             subtotal = item.product.price * item.quantity
#             total += subtotal
#             cart_items.append({
#                 'product': item.product,
#                 'quantity': item.quantity,
#                 'subtotal': subtotal,
#             })
#     else:
#         # Use session cart for guests
#         cart = request.session.get('cart', {})
#         for product_id, quantity in cart.items():
#             product = get_object_or_404(Product, id=product_id)
#             subtotal = product.price * quantity
#             total += subtotal
#             cart_items.append({
#                 'product': product,
#                 'quantity': quantity,
#                 'subtotal': subtotal,
#             })

#     return render(request, 'checkout.html', {
#         'cart_items': cart_items,
#         'total': total
#     })

def place_order_view(request):
    if request.method == 'POST':
        # Extract form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')

        cart_items = []
        total = 0

        if request.user.is_authenticated:
            # Use DB cart
            db_cart = CartItem.objects.filter(cart__user=request.user)
            if not db_cart.exists():
                return redirect('cart')

            for item in db_cart:
                subtotal = item.product.price * item.quantity
                total += subtotal
                color_name = f" ({item.color.name})" if item.color else ""
                cart_items.append({
                    'title': f"{item.product.title}{color_name}",
                    'quantity': item.quantity,
                    'subtotal': subtotal,
                })

        else:
            # Use session cart
            session_cart = request.session.get('cart', {})
            if not session_cart:
                return redirect('cart')

            for key, quantity in session_cart.items():
                try:
                    product_id, color_id = key.split('_')
                    product = Product.objects.get(id=product_id)
                    color = Color.objects.get(id=color_id)
                    color_name = f" ({color.name})"
                except Exception:
                    # fallback if color or key is invalid
                    product = Product.objects.get(id=key if '_' not in key else key.split('_')[0])
                    color_name = ""

                subtotal = product.price * quantity
                total += subtotal
                cart_items.append({
                    'title': f"{product.title}{color_name}",
                    'quantity': quantity,
                    'subtotal': subtotal,
                })

        # Compose WhatsApp message
        message_lines = [
            f"📦 *New Order Received!*",
            f"👤 Name: {first_name} {last_name}",
            f"📧 Email: {email}",
            f"🏠 Address: {address}, {city}, {postal_code}",
            "\n🛒 *Items:*"
        ]
        for item in cart_items:
            message_lines.append(f"- {item['title']} x{item['quantity']} = PKR {item['subtotal']:.0f}")

        message_lines.append(f"\n💰 *Total:* PKR {total:.0f}")
        message_lines.append(f"\n🚚 *Thank you for ordering with PhoneTech!*")

        message = "\n".join(message_lines)
        whatsapp_number = '923106958010'
        whatsapp_link = f"https://wa.me/{whatsapp_number}?text={quote(message)}"

        request.session['whatsapp_link'] = whatsapp_link

        # Clear cart
        if request.user.is_authenticated:
            CartItem.objects.filter(cart__user=request.user).delete()
        else:
            request.session['cart'] = {}

        return redirect('order_success')


# def place_order_view(request):
#     if request.method == 'POST':
#         # Extract form data
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         address = request.POST.get('address')
#         city = request.POST.get('city')
#         postal_code = request.POST.get('postal_code')

#         cart_items = []
#         total = 0

#         if request.user.is_authenticated:
#             # Use DB cart
#             db_cart = CartItem.objects.filter(cart__user=request.user)

#             if not db_cart.exists():
#                 return redirect('cart')
#             for item in db_cart:
#                 subtotal = item.product.price * item.quantity
#                 total += subtotal
#                 cart_items.append({
#                     'title': f"{item.product.title} ({item.color.name})" if item.color else item.product.title,
#                     'quantity': item.quantity,
#                     'subtotal': subtotal,
#                 })
#         else:
#             # Use session cart
#             session_cart = request.session.get('cart', {})
#             if not session_cart:
#                 return redirect('cart')
#             for product_id, quantity in session_cart.items():
#                 product = Product.objects.get(id=product_id)
#                 subtotal = product.price * quantity
#                 total += subtotal
#                 cart_items.append({
#                     'title': f"{item.product.title} ({item.color.name})" if item.color else item.product.title,
#                     'quantity': quantity,
#                     'subtotal': subtotal,
#                 })

#         # Compose WhatsApp message
#         message_lines = [
#             f"📦 *New Order Received!*",
#             f"👤 Name: {first_name} {last_name}",
#             f"📧 Email: {email}",
#             f"🏠 Address: {address}, {city}, {postal_code}",
#             "\n🛒 *Items:*"
#         ]
#         for item in cart_items:
#             message_lines.append(f"- {item['title']} x{item['quantity']} = PKR {item['subtotal']}")

#         message_lines.append(f"\n💰 *Total:* PKR {total}")
#         message_lines.append(f"\n🚚 *Thank you for ordering with PhoneTech!*")

#         message = "\n".join(message_lines)
#         whatsapp_number = '923106958010'
#         whatsapp_link = f"https://wa.me/{whatsapp_number}?text={quote(message)}"

#         request.session['whatsapp_link'] = whatsapp_link

#         # Clear cart
#         if request.user.is_authenticated:
#             CartItem.objects.filter(cart__user=request.user).delete()

#         else:
#             request.session['cart'] = {}

#         return redirect('order_success')

def order_success_view(request):
    # Pop the WhatsApp link from session (removes it after use)
    whatsapp_link = request.session.pop('whatsapp_link', None)

    return render(request, 'order_success.html', {'whatsapp_link': whatsapp_link})

def about_view(request):
    return render(request, 'about.html')

def warranty_view(request):
    return render(request, 'warranty.html')

def contact_view(request):
    return render(request, 'contact.html')



def refund_policy_view(request):
    return render(request, 'refund.html')

def terms_conditions_view(request):
    return render(request, 'terms.html')