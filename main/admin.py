from django.contrib import admin
from .models import Product, Cart, CartItem, Order, Review, Color
from django import forms

# admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Review)
# admin.site.register(Color)
class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ('colors',)  # If using ManyToMany
admin.site.register(Product, ProductAdmin)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex']


