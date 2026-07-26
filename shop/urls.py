from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("favorites/toggle/<int:product_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.favorites_list, name="favorites_list"),
]