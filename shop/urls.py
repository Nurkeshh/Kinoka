from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/increase/<int:product_id>/", views.increase_cart_quantity, name="increase_cart_quantity"),
    path("cart/decrease/<int:product_id>/", views.decrease_cart_quantity, name="decrease_cart_quantity"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/promo/apply/", views.apply_promo, name="apply_promo"),
    path("cart/promo/remove/", views.remove_promo, name="remove_promo"),
    path("checkout/", views.checkout, name="checkout"),
    path("pay/<int:order_id>/", views.pay_kaspi, name="pay_kaspi"),
    path("request/<int:product_id>/", views.product_request_view, name="product_request"),
    path("favorites/toggle/<int:product_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.favorites_list, name="favorites_list"),
    path("compare/toggle/<int:product_id>/", views.toggle_compare, name="toggle_compare"),
    path("compare/", views.compare_view, name="compare_view"),
    path("city/set/<str:slug>/", views.set_city, name="set_city"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("feedback/", views.feedback_view, name="feedback"),
]