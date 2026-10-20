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
    help = "Добавляет недостающие товары бренда Kinoka"

    def handle(self, *args, **options):
        categories_data = ["Пылесосы", "Инструменты", "Тренажёры", "Массажёры", "Пароочистители", "Бытовая техника"]
        categories = {}
        for name in categories_data:
            slug = translit_slugify(name)
            category, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            categories[name] = category

        # (название, категория, цена, месяцев рассрочки, кол-во отзывов)
        products_data = [
            ("Массажер Kinoka 01-012 ручной 3D-массаж, вибрационный", "Массажёры", 14990, 3, 186),
            ("Велотренажер Kinoka вертикальный", "Тренажёры", 69990, 12, 121),
            ("Пароочиститель Kinoka 18-013 черный", "Пароочистители", 22490, 6, 149),
            ("Электрорубанок Kinoka 20-031", "Инструменты", 19990, 6, 91),
            ("Пароочиститель Kinoka 18-004 бирюзовый", "Пароочистители", 21990, 6, 955),

            ("Kinoka 18-012 черный, желтый", "Пылесосы", 32900, 12, 62),
            ("Шлифмашина угловая Kinoka 20-113", "Инструменты", 31990, 12, 248),
            ("Шлифмашина угловая Kinoka 20-133", "Инструменты", 31490, 12, 28),
            ("Маникюрный аппарат Kinoka STE101", "Массажёры", 16990, 6, 88),

            ("Степпер Kinoka 27-011 лестничный", "Тренажёры", 47990, 12, 82),
            ("Аккумуляторная цепная пила Kinoka 20-030", "Инструменты", 29990, 12, 67),
            ("Беговая дорожка Kinoka 27-006 электрическая", "Тренажёры", 86990, 12, 118),

            ("Шлифмашина эксцентриковая Kinoka 20-028", "Инструменты", 14990, 3, 212),
            ("Увлажнитель воздуха Kinoka 28-001 белый", "Бытовая техника", 29590, 12, 37),
            ("Kinoka 18-014 белый, черный", "Пылесосы", 49990, 12, 45),
            ("Тренажер-платформа Kinoka 27-017", "Тренажёры", 62990, 12, 40),
            ("Электросамокат детский Kinoka 12-003 черный", "Бытовая техника", 88990, 12, 18),
            ("Электрическая цепная пила Kinoka 20-020", "Инструменты", 44900, 12, 31),

            ("Степпер Kinoka 27-016 балансировочный", "Тренажёры", 26990, 12, 203),
            ("Автопылесос Kinoka 06-020 черный", "Пылесосы", 33990, 12, 215),

            ("Kinoka дрель-шуруповерт 20-023 18В", "Инструменты", 9900, 3, 29),
            ("Kinoka 06-023 черный", "Пылесосы", 59990, 12, 32),
            ("Пароочиститель Kinoka 18-003 белый", "Пароочистители", 22990, 6, 71),
            ("Очиститель воздуха Kinoka 28-002 белый", "Бытовая техника", 39990, 12, 244),
            ("Сабельная пила Kinoka 20-026", "Инструменты", 27990, 12, 287),
            ("Пароочиститель Kinoka 18-002 белый", "Пароочистители", 22490, 6, 150),
        ]

        created_count = 0
        for name, category_name, price, months, reviews in products_data:
            slug = translit_slugify(name)
            _, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": categories[category_name],
                    "price": price,
                    "installment_months": months,
                    "rating": 5.0,
                    "reviews_count": reviews,
                    "stock": 10,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Добавлено новых товаров: {created_count}"))