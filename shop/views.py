from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Product, Category, Order, OrderItem, Review, Subscriber, Feedback, PromoCode, ProductRequest
from .context_processors import CITIES


def home(request):
    category_slug = request.GET.get("category")
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "")
    price_min = request.GET.get("price_min", "")
    price_max = request.GET.get("price_max", "")
    min_rating = request.GET.get("min_rating", "")
    categories = Category.objects.all()

    products = Product.objects.all()
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if query:
        products = products.filter(name__icontains=query)
    if price_min.isdigit():
        products = products.filter(price__gte=price_min)
    if price_max.isdigit():
        products = products.filter(price__lte=price_max)
    if min_rating.isdigit():
        products = products.filter(rating__gte=min_rating)

    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "rating":
        products = products.order_by("-rating")
    elif sort == "newest":
        products = products.order_by("-created_at")

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    products_page = paginator.get_page(page_number)

    favorites = request.session.get("favorites", [])
    compare = request.session.get("compare", [])

    return render(request, "shop/home.html", {
        "products": products_page,
        "categories": categories,
        "current_category": category_slug,
        "favorites": favorites,
        "compare_list": compare,
        "query": query,
        "current_sort": sort,
        "price_min": price_min,
        "price_max": price_max,
        "min_rating": min_rating,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    favorites = request.session.get("favorites", [])
    compare = request.session.get("compare", [])

    viewed = request.session.get("viewed_products", [])
    if product.id not in viewed:
        product.view_count += 1
        product.save(update_fields=["view_count"])
        viewed.append(product.id)
        request.session["viewed_products"] = viewed

    if request.method == "POST":
        Review.objects.create(
            product=product,
            name=request.POST.get("name", "Аноним"),
            text=request.POST.get("text", ""),
            rating=int(request.POST.get("rating", 5)),
        )
        messages.success(request, "Спасибо за отзыв!")
        return redirect("product_detail", slug=product.slug)

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:6]

    return render(request, "shop/product_detail.html", {
        "product": product,
        "favorites": favorites,
        "compare_list": compare,
        "related_products": related_products,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get("cart", {})
    product_id_str = str(product_id)
    current_qty = cart.get(product_id_str, 0)

    if current_qty < product.stock:
        cart[product_id_str] = current_qty + 1
        request.session["cart"] = cart
        messages.success(request, f"«{product.name}» добавлен в корзину")
    else:
        messages.error(request, "Товара нет в наличии в нужном количестве")

    return redirect(request.META.get("HTTP_REFERER", "home"))


def increase_cart_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    current_qty = cart.get(product_id, 0)

    if current_qty < product.stock:
        cart[product_id] = current_qty + 1
        request.session["cart"] = cart

    return redirect("cart_detail")


def decrease_cart_quantity(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    if product_id in cart:
        cart[product_id] -= 1
        if cart[product_id] <= 0:
            del cart[product_id]
        request.session["cart"] = cart
    return redirect("cart_detail")


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

    promo = request.session.get("promo")
    discount_percent = promo.get("discount_percent", 0) if promo else 0
    discounted_total = round(total * (100 - discount_percent) / 100, 2) if discount_percent else total

    return render(request, "shop/cart.html", {
        "items": items,
        "total": total,
        "discounted_total": discounted_total,
        "promo": promo,
    })


@require_POST
def apply_promo(request):
    code = request.POST.get("promo_code", "").strip().upper()
    try:
        promo = PromoCode.objects.get(code=code, active=True)
        request.session["promo"] = {"code": promo.code, "discount_percent": promo.discount_percent}
        messages.success(request, f"Промокод применён: -{promo.discount_percent}%")
    except PromoCode.DoesNotExist:
        messages.error(request, "Промокод не найден или недействителен")
    return redirect("cart_detail")


def remove_promo(request):
    request.session.pop("promo", None)
    return redirect("cart_detail")


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


def toggle_compare(request, product_id):
    compare = request.session.get("compare", [])
    product_id = int(product_id)
    if product_id in compare:
        compare.remove(product_id)
    else:
        if len(compare) >= 4:
            messages.error(request, "Можно сравнивать максимум 4 товара")
        else:
            compare.append(product_id)
    request.session["compare"] = compare
    return redirect(request.META.get("HTTP_REFERER", "home"))


def compare_view(request):
    compare = request.session.get("compare", [])
    products = Product.objects.filter(id__in=compare)

    spec_names = []
    for product in products:
        for spec in product.specifications.all():
            if spec.name not in spec_names:
                spec_names.append(spec.name)

    return render(request, "shop/compare.html", {"products": products, "spec_names": spec_names})


def set_city(request, slug):
    if slug in CITIES:
        request.session["city"] = slug
    return redirect(request.META.get("HTTP_REFERER", "home"))


def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("home")

    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})

    promo = request.session.get("promo")
    discount_percent = promo.get("discount_percent", 0) if promo else 0
    discounted_total = round(total * (100 - discount_percent) / 100, 2) if discount_percent else total

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=request.POST.get("name", ""),
            customer_phone=request.POST.get("phone", ""),
            address=request.POST.get("address", ""),
            promo_code=promo.get("code", "") if promo else "",
            discount_percent=discount_percent,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=item["product"].price,
            )
            item["product"].stock -= item["quantity"]
            item["product"].save()

        request.session["cart"] = {}
        request.session.pop("promo", None)
        return redirect("pay_kaspi", order_id=order.id)

    return render(request, "shop/checkout.html", {
        "items": items,
        "total": total,
        "discounted_total": discounted_total,
        "promo": promo,
    })


def pay_kaspi(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "shop/pay_kaspi.html", {
        "order": order,
        "kaspi_phone": settings.STORE_KASPI_PHONE,
    })


def product_request_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        ProductRequest.objects.create(
            product=product,
            name=request.POST.get("name", ""),
            phone=request.POST.get("phone", ""),
        )
        messages.success(request, "Заявка принята! Мы сообщим вам, когда товар появится.")
        return redirect("product_detail", slug=product.slug)

    return render(request, "shop/product_request.html", {"product": product})


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            messages.error(request, "Заполните все поля")
        elif len(password) < 8:
            messages.error(request, "Пароль должен быть не короче 8 символов")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Такой пользователь уже существует")
        else:
            user = User.objects.create_user(username=username, password=password)
            auth_login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("home")
    return render(request, "shop/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("home")
        messages.error(request, "Неверный логин или пароль")
    return render(request, "shop/login.html")


def logout_view(request):
    auth_logout(request)
    return redirect("home")


def my_orders(request):
    if not request.user.is_authenticated:
        return redirect("login")
    orders = request.user.orders.all().order_by("-created_at")
    return render(request, "shop/my_orders.html", {"orders": orders})


def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email:
            Subscriber.objects.get_or_create(email=email)
            messages.success(request, "Вы подписались на рассылку!")
    return redirect(request.META.get("HTTP_REFERER", "home"))


def feedback_view(request):
    if request.method == "POST":
        Feedback.objects.create(
            name=request.POST.get("name", ""),
            contact=request.POST.get("contact", ""),
            subject=request.POST.get("subject", ""),
            message=request.POST.get("message", ""),
        )
        messages.success(request, "Сообщение отправлено, мы свяжемся с вами.")
        return redirect("feedback")
    return render(request, "shop/feedback.html")