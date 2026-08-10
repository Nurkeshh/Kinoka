from django.contrib import admin
from .models import (
    Category, Product, ProductImage, Specification, Review,
    Subscriber, Feedback, PromoCode, ProductRequest, Order, OrderItem
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 3


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "rating", "reviews_count", "kaspi_url")
    inlines = [ProductImageInline, SpecificationInline, ReviewInline]


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "contact", "created_at")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "status", "created_at")
    list_editable = ("status",)


class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "phone", "created_at")


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Subscriber)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(PromoCode)
admin.site.register(ProductRequest, ProductRequestAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)