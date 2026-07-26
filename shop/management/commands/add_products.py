from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category, Product

TRANSLIT_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def translit_slugify(text):
    result = ""
    for char in text.lower():
        result += TRANSLIT_MAP.get(char, char)
    return slugify(result)


class Command(BaseCommand):
    help = "Добавляет тестовые товары без фото"

    def handle(self, *args, **options):
        categories_data = ["Пылесосы", "Инструменты", "Тренажёры", "Массажёры"]
        categories = {}
        for name in categories_data:
            slug = translit_slugify(name)
            category, _ = Category.objects.get_or_create(
                slug=slug, defaults={"name": name}
            )
            categories[name] = category

        products_data = [
            ("Kinoka P8 красный", "Пылесосы", 42990),
            ("Kinoka 18-006 белый", "Пылесосы", 39990),
            ("Kinoka V8 фиолетовый", "Пылесосы", 42990),
            ("Пароочиститель Kinoka 18-010 черный", "Пылесосы", 21990),
            ("Шлифмашина угловая Kinoka 20-013", "Инструменты", 29990),
            ("Перфоратор аккумуляторный Kinoka 20-027", "Инструменты", 32900),
            ("Kinoka шуруповерт 20-007", "Инструменты", 16900),
            ("Кусторез Kinoka 20-012", "Инструменты", 38990),
            ("Степпер Kinoka 27-015 лестничный", "Тренажёры", 47990),
            ("Kinoka 27-003 классический", "Тренажёры", 26990),
            ("Беговая дорожка Kinoka 27-010", "Тренажёры", 113990),
            ("Велотренажер Kinoka портативный", "Тренажёры", 49990),
            ("Массажер Kinoka 17-007 напольный", "Массажёры", 47990),
            ("Массажер Kinoka 17-001 вибрационный", "Массажёры", 37990),
            ("Массажер Kinoka 01-003 ручной 3D", "Массажёры", 19990),
        ]

        created_count = 0
        for name, category_name, price in products_data:
            slug = translit_slugify(name)
            _, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": categories[category_name],
                    "price": price,
                    "stock": 10,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Добавлено товаров: {created_count}"))