import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from shop.models import Category, Product, Specification, Review


def read_csv(filename):
    path = os.path.join(settings.BASE_DIR, "data", filename)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


class Command(BaseCommand):
    help = "Импортирует товары, характеристики и отзывы из CSV в data/"

    def handle(self, *args, **options):
        products_created = 0
        products_updated = 0

        for row in read_csv("products.csv"):
            category, _ = Category.objects.get_or_create(
                name=row["category"].strip(),
                defaults={"slug": row["category"].strip().lower().replace(" ", "-")},
            )

            defaults = {
                "name": row["name"].strip(),
                "category": category,
                "price": row["price"].strip(),
                "old_price": row["old_price"].strip() or None,
                "description": row.get("description", "").strip(),
                "rating": row.get("rating", "5").strip() or 5,
                "reviews_count": row.get("reviews_count", "0").strip() or 0,
                "stock": row.get("stock", "10").strip() or 10,
            }

            product, created = Product.objects.update_or_create(
                slug=row["slug"].strip(), defaults=defaults
            )
            if created:
                products_created += 1
            else:
                products_updated += 1

        specs_created = 0
        for row in read_csv("specs.csv"):
            try:
                product = Product.objects.get(slug=row["product_slug"].strip())
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Товар не найден для характеристики: {row['product_slug']}"))
                continue

            _, created = Specification.objects.get_or_create(
                product=product,
                name=row["spec_name"].strip(),
                defaults={"value": row["spec_value"].strip()},
            )
            if created:
                specs_created += 1

        reviews_created = 0
        for row in read_csv("reviews.csv"):
            try:
                product = Product.objects.get(slug=row["product_slug"].strip())
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Товар не найден для отзыва: {row['product_slug']}"))
                continue

            _, created = Review.objects.get_or_create(
                product=product,
                name=row["name"].strip(),
                text=row["text"].strip(),
                defaults={"rating": row.get("rating", "5").strip() or 5},
            )
            if created:
                reviews_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Товары: создано {products_created}, обновлено {products_updated}. "
            f"Характеристик добавлено: {specs_created}. Отзывов добавлено: {reviews_created}."
        ))