from .models import Category, Product

CITIES = {
    "almaty": {"name": "Алматы", "x": 400, "y": 250},
    "astana": {"name": "Астана", "x": 320, "y": 100},
    "shymkent": {"name": "Шымкент", "x": 270, "y": 250},
    "karaganda": {"name": "Караганда", "x": 330, "y": 150},
    "aktobe": {"name": "Актобе", "x": 140, "y": 120},
    "taraz": {"name": "Тараз", "x": 300, "y": 240},
    "pavlodar": {"name": "Павлодар", "x": 420, "y": 90},
    "ust-kamenogorsk": {"name": "Усть-Каменогорск", "x": 520, "y": 110},
    "semey": {"name": "Семей", "x": 470, "y": 90},
    "atyrau": {"name": "Атырау", "x": 60, "y": 170},
    "kostanay": {"name": "Костанай", "x": 200, "y": 70},
    "kyzylorda": {"name": "Кызылорда", "x": 220, "y": 200},
    "uralsk": {"name": "Уральск", "x": 80, "y": 90},
    "petropavlovsk": {"name": "Петропавловск", "x": 260, "y": 40},
    "aktau": {"name": "Актау", "x": 40, "y": 230},
    "kokshetau": {"name": "Кокшетау", "x": 280, "y": 70},
}


def categories_processor(request):
    cart = request.session.get("cart", {})
    favorites = request.session.get("favorites", [])
    compare = request.session.get("compare", [])

    valid_favorites_count = Product.objects.filter(id__in=favorites).count()
    valid_compare_count = Product.objects.filter(id__in=compare).count()

    city_slug = request.session.get("city", "almaty")
    selected_city = CITIES.get(city_slug, CITIES["almaty"])["name"]

    return {
        "all_categories": Category.objects.all(),
        "cart_count": sum(cart.values()),
        "favorites_count": valid_favorites_count,
        "compare_count": valid_compare_count,
        "cities": CITIES,
        "selected_city": selected_city,
        "selected_city_slug": city_slug,
    }