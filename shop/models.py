from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    reviews_count = models.PositiveIntegerField(default=0)
    installment_months = models.PositiveIntegerField(default=12)
    variant_group = models.CharField(max_length=100, blank=True)
    variant_label = models.CharField(max_length=50, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    kaspi_url = models.URLField(blank=True, help_text="Ссылка на товар на Kaspi.kz")
    created_at = models.DateTimeField(auto_now_add=True)

    def installment_price(self):
        if self.installment_months:
            return round(self.price / self.installment_months)
        return self.price

    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - self.price / self.old_price) * 100)
        return 0

    def in_stock(self):
        return self.stock > 0

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return self.rating

    def total_reviews(self):
        count = self.reviews.count()
        return count if count > 0 else self.reviews_count

    def variants(self):
        if self.variant_group:
            return Product.objects.filter(variant_group=self.variant_group).exclude(id=self.id)
        return Product.objects.none()

    def is_bestseller(self):
        return self.view_count >= 50

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/gallery/")

    def __str__(self):
        return f"Фото для {self.product.name}"


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specifications")
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}: {self.value}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.name} на {self.product.name}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=150)
    subject = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.subject or 'Без темы'}"


class PromoCode(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} (-{self.discount_percent}%)"


class ProductRequest(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="requests")
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заявка на {self.product.name} от {self.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает подтверждения"),
        ("processing", "Собирается"),
        ("shipped", "В пути"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменён"),
    ]

    STATUS_STEPS = ["pending", "processing", "shipped", "delivered"]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    promo_code = models.CharField(max_length=30, blank=True)
    discount_percent = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        subtotal = sum(item.subtotal() for item in self.items.all())
        if self.discount_percent:
            subtotal = subtotal * (100 - self.discount_percent) / 100
        return round(subtotal, 2)

    def status_progress(self):
        if self.status == "cancelled":
            return 0
        try:
            return self.STATUS_STEPS.index(self.status) + 1
        except ValueError:
            return 1

    def __str__(self):
        return f"Order #{self.id} — {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"