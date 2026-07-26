from django.contrib import admin
from .models import Category, Product, Order, OrderItem


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "rating", "reviews_count", "stock")


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)