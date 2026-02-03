from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="دسته‌بندی")
    slug = models.SlugField(max_length=140, unique=True, verbose_name="اسلاگ")

    class Meta:
        ordering = ["name"]
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="دسته‌بندی")
    name = models.CharField(max_length=220, verbose_name="نام محصول")
    slug = models.SlugField(unique=True, verbose_name="اسلاگ")
    description = models.TextField(verbose_name="توضیحات")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت")
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="قیمت قبل")
    image = models.ImageField(upload_to="products/", verbose_name="تصویر اصلی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("4.6"), verbose_name="امتیاز")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def discount_percent(self):
        if self.compare_at_price and self.compare_at_price > 0:
            return round((1 - (self.price / self.compare_at_price)) * 100)
        return 0

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("shop:product_detail", kwargs={"slug": self.slug})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery", verbose_name="محصول")
    image = models.ImageField(upload_to="products/gallery/", verbose_name="تصویر")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="متن جایگزین")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "تصویر گالری"
        verbose_name_plural = "تصاویر گالری"

    def __str__(self):
        return f"{self.product.name} #{self.sort_order}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار پرداخت"),
        ("processing", "در حال پردازش"),
        ("shipped", "ارسال شده"),
        ("delivered", "تحویل شده"),
        ("cancelled", "لغو شده"),
    ]

    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, related_name="orders", verbose_name="کاربر")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="وضعیت")
    full_name = models.CharField(max_length=180, verbose_name="نام و نام خانوادگی")
    email = models.EmailField(verbose_name="ایمیل")
    address = models.CharField(max_length=255, verbose_name="آدرس")
    city = models.CharField(max_length=100, verbose_name="شهر")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی")
    country = models.CharField(max_length=80, default="ایران", verbose_name="کشور")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="جمع جزء")
    shipping = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="هزینه ارسال")
    tax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مالیات")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ کل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

    def __str__(self):
        return f"سفارش #{self.id}"

    @property
    def order_number(self):
        return f"EC-{self.id:06d}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="سفارش")
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL, related_name="order_items", verbose_name="محصول")
    name = models.CharField(max_length=220, verbose_name="نام محصول")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت واحد")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.price * self.quantity

# Create your models here.
