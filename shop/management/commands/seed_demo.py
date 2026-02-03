from decimal import Decimal
from pathlib import Path
from random import randint

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from shop.models import Category, Product, ProductImage

CATEGORIES = [
    "\u06a9\u0627\u0644\u0627\u06cc \u062f\u06cc\u062c\u06cc\u062a\u0627\u0644",  # کالای دیجیتال
    "\u0645\u062f \u0648 \u067e\u0648\u0634\u0627\u06a9",  # مد و پوشاک
    "\u062e\u0627\u0646\u0647 \u0648 \u0622\u0634\u067e\u0632\u062e\u0627\u0646\u0647",  # خانه و آشپزخانه
    "\u0632\u06cc\u0628\u0627\u06cc\u06cc \u0648 \u0633\u0644\u0627\u0645\u062a",  # زیبایی و سلامت
    "\u0648\u0631\u0632\u0634 \u0648 \u0633\u0641\u0631",  # ورزش و سفر
]

PRODUCTS = [
    ("\u0647\u062f\u0641\u0648\u0646 \u0646\u0648\u06cc\u0632\u06a9\u0646\u0633\u0644\u06cc\u0646\u06af \u0622\u0644\u0641\u0627", "\u06a9\u0627\u0644\u0627\u06cc \u062f\u06cc\u062c\u06cc\u062a\u0627\u0644", 4890000, 5490000),
    ("\u0633\u0627\u0639\u062a \u0647\u0648\u0634\u0645\u0646\u062f \u0644\u0627\u06cc\u062a", "\u06a9\u0627\u0644\u0627\u06cc \u062f\u06cc\u062c\u06cc\u062a\u0627\u0644", 3290000, 3890000),
    ("\u06a9\u0641\u0634 \u0631\u0627\u0646\u06cc\u0646\u06af \u0641\u0644\u06a9\u0633", "\u0648\u0631\u0632\u0634 \u0648 \u0633\u0641\u0631", 2190000, 2590000),
    ("\u06a9\u062a \u0628\u0627\u0631\u0627\u0646\u06cc \u0636\u062f\u0622\u0628", "\u0645\u062f \u0648 \u067e\u0648\u0634\u0627\u06a9", 1890000, 2190000),
    ("\u0628\u0644\u0646\u062f\u06af\u0648 \u0628\u0644\u0648\u062a\u0648\u062b\u06cc \u0645\u06cc\u0646\u06cc", "\u06a9\u0627\u0644\u0627\u06cc \u062f\u06cc\u062c\u06cc\u062a\u0627\u0644", 1290000, 1590000),
    ("\u0632\u0648\u062f\u067e\u0632 \u0627\u0633\u062a\u06cc\u0644 ۶ \u0644\u06cc\u062a\u0631\u06cc", "\u062e\u0627\u0646\u0647 \u0648 \u0622\u0634\u067e\u0632\u062e\u0627\u0646\u0647", 2490000, 2890000),
    ("\u0645\u0627\u0633\u06a9 \u0635\u0648\u0631\u062a \u0622\u0628\u0631\u0633\u0627\u0646", "\u0632\u06cc\u0628\u0627\u06cc\u06cc \u0648 \u0633\u0644\u0627\u0645\u062a", 189000, 239000),
    ("\u06a9\u06cc\u062a \u062f\u0645\u0628\u0644 \u0642\u0627\u0628\u0644 \u062a\u0646\u0638\u06cc\u0645", "\u0648\u0631\u0632\u0634 \u0648 \u0633\u0641\u0631", 1590000, 1890000),
    ("\u06a9\u062a\u0627\u0646\u06cc \u0631\u0648\u0632\u0645\u0631\u0647 \u0627\u062f\u0648\u0646\u0686\u0631", "\u0645\u062f \u0648 \u067e\u0648\u0634\u0627\u06a9", 2790000, 3190000),
    ("\u06af\u0644\u062f\u0627\u0646 \u0633\u0631\u0627\u0645\u06cc\u06a9\u06cc \u062f\u06a9\u0648\u0631", "\u062e\u0627\u0646\u0647 \u0648 \u0622\u0634\u067e\u0632\u062e\u0627\u0646\u0647", 349000, 0),
    ("\u0633\u062a \u0628\u0631\u0627\u0634 \u0622\u0631\u0627\u06cc\u0634\u06cc ۱۰ \u062a\u06a9\u0647", "\u0632\u06cc\u0628\u0627\u06cc\u06cc \u0648 \u0633\u0644\u0627\u0645\u062a", 490000, 590000),
    ("\u06a9\u0648\u0644\u0647 \u067e\u0634\u062a\u06cc \u0645\u0633\u0627\u0641\u0631\u062a\u06cc", "\u0648\u0631\u0632\u0634 \u0648 \u0633\u0641\u0631", 1390000, 1690000),
    ("\u0647\u0648\u062f\u06cc \u0627\u0633\u067e\u0631\u062a \u0646\u0631\u0645", "\u0645\u062f \u0648 \u067e\u0648\u0634\u0627\u06a9", 1290000, 1490000),
    ("\u0645\u0627\u0646\u06cc\u062a\u0648\u0631 ۲۷ \u0627\u06cc\u0646\u0686 QHD", "\u06a9\u0627\u0644\u0627\u06cc \u062f\u06cc\u062c\u06cc\u062a\u0627\u0644", 9890000, 0),
    ("\u0686\u0631\u0627\u063a \u0645\u0637\u0627\u0644\u0639\u0647 \u0645\u06cc\u0646\u06cc\u0645\u0627\u0644", "\u062e\u0627\u0646\u0647 \u0648 \u0622\u0634\u067e\u0632\u062e\u0627\u0646\u0647", 690000, 890000),
]

class Command(BaseCommand):
    help = "Seed demo categories and products with placeholder images"

    def handle(self, *args, **options):
        media_root = Path("media/seed")
        media_root.mkdir(parents=True, exist_ok=True)

        category_objs = {}
        for name in CATEGORIES:
            slug = slugify(name, allow_unicode=True)
            obj, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            category_objs[name] = obj

        for name, cat_name, price, compare in PRODUCTS:
            category = category_objs[cat_name]
            slug = slugify(name, allow_unicode=True)
            image_path = media_root / f"{slug}.jpg"
            if not image_path.exists():
                self._create_placeholder(image_path, name)
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "category": category,
                    "description": f"\u062a\u0648\u0636\u06cc\u062d\u0627\u062a \u0646\u0645\u0648\u0646\u0647 \u0628\u0631\u0627\u06cc {name}.",
                    "price": Decimal(price),
                    "compare_at_price": Decimal(compare) if compare else None,
                    "image": f"seed/{image_path.name}",
                    "is_active": True,
                },
            )
            if created:
                ProductImage.objects.create(
                    product=product,
                    image=f"seed/{image_path.name}",
                    alt_text=name,
                    sort_order=0,
                )
        self.stdout.write(self.style.SUCCESS("Seed data created."))

    def _create_placeholder(self, path: Path, text: str):
        width, height = 900, 1100
        color = (randint(80, 140), randint(160, 220), randint(120, 200))
        img = Image.new("RGB", (width, height), color)
        draw = ImageDraw.Draw(img)
        short = text[:18]
        try:
            font = ImageFont.truetype("arial.ttf", 42)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), short, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((width - text_width) / 2, (height - text_height) / 2), short, fill=(255, 255, 255), font=font)
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format="JPEG", quality=85)
