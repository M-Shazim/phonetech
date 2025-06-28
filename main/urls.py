from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('admin/', admin.site.urls),

    path('clear-whatsapp/', clear_whatsapp_session, name='clear_whatsapp_session'),


    # Core pages
    path('', home_view, name='home'),
    path('products/', product_list_view, name='products'),
    path('products/<int:id>/', product_detail_view, name='product_detail'),
    path('products/<int:id>/add-review/', add_review, name='add_review'),

    # Cart
    path('cart/', cart_view, name='cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('cart/update/<int:product_id>/', update_cart, name='update_cart_item'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('add-to-cart/<int:id>/', add_to_cart_view, name='add_to_cart'),

    # Checkout
    path('checkout/', checkout_view, name='checkout'),
    path('place-order/', place_order_view, name='place_order'),
    path('order-success/', order_success_view, name='order_success'),

    # Static info pages
    path('about/', about_view, name='about'),
    path('warranty/', warranty_view, name='warranty'),
    path('contact/', contact_view, name='contact'),
    path('refund/', refund_policy_view, name='refund'),
    path('terms/', terms_conditions_view, name='terms'),
    path('cancellation-policy/', cancellation_policy, name='cancellation_policy'),
    path('delivery-policy/', delivery_policy, name='delivery_policy'),


    # Auth
    # path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', signup_view, name='signup'),
    path('account/', account_view, name='account'),

    # Optional: Search
    path('search/', search_view, name='search'),  # if you have implemented search_view

    path('privacy-policy/', privacy_policy_view, name='privacy_policy'),
    path('faq/', faq_view, name='faq'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
