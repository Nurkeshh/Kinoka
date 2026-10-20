from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/promo/apply/", views.apply_promo, name="apply_promo"),
    path("cart/promo/remove/", views.remove_promo, name="remove_promo"),
    path("checkout/", views.checkout, name="checkout"),
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