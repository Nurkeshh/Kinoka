import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from shop.models import Product, Specification, Review


class Command(BaseCommand):
    help = "Экспортирует текущие товары, характеристики и отзывы из базы в CSV"

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, "data")
        os.makedirs(data_dir, exist_ok=True)

        with open(os.path.join(data_dir, "products.csv"), "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["slug", "name", "category", "price", "old_price", "description", "rating", "reviews_count", "stock"])
            for p in Product.objects.all():
                writer.writerow([
                    p.slug, p.name, p.category.name, p.price,
                    p.old_price or "", p.description, p.rating, p.reviews_count, p.stock,
                ])

        with open(os.path.join(data_dir, "specs.csv"), "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["product_slug", "spec_name", "spec_value"])
            for s in Specification.objects.select_related("product").all():
                writer.writerow([s.product.slug, s.name, s.value])

        with open(os.path.join(data_dir, "reviews.csv"), "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["product_slug", "name", "text", "rating"])
            for r in Review.objects.select_related("product").all():
                writer.writerow([r.product.slug, r.name, r.text, r.rating])

        self.stdout.write(self.style.SUCCESS("Экспорт готов: data/products.csv, data/specs.csv, data/reviews.csv"))