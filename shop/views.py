from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category


def home(request):
    category_slug = request.GET.get("category")
    query = request.GET.get("q", "").strip()
    categories = Category.objects.all()

    products = Product.objects.all()
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(name__icontains=query)

    favorites = request.session.get("favorites", [])

    return render(request, "shop/home.html", {
        "products": products,
        "categories": categories,
        "current_category": category_slug,
        "favorites": favorites,
        "query": query,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    favorites = request.session.get("favorites", [])
    return render(request, "shop/product_detail.html", {
        "product": product,
        "favorites": favorites,
    })


def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session["cart"] = cart
    return redirect(request.META.get("HTTP_REFERER", "home"))


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
    request.session["cart"] = cart
    return redirect("cart_detail")


def cart_detail(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})

    return render(request, "shop/cart.html", {"items": items, "total": total})


def toggle_favorite(request, product_id):
    favorites = request.session.get("favorites", [])
    product_id = int(product_id)
    if product_id in favorites:
        favorites.remove(product_id)
    else:
        favorites.append(product_id)
    request.session["favorites"] = favorites
    return redirect(request.META.get("HTTP_REFERER", "home"))


def favorites_list(request):
    favorites = request.session.get("favorites", [])
    products = Product.objects.filter(id__in=favorites)
    return render(request, "shop/favorites.html", {"products": products, "favorites": favorites})