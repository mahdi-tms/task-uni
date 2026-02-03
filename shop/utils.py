from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple

from .models import Product


def get_cart(session) -> dict:
    return session.get("cart", {})


def save_cart(request, cart: dict):
    request.session["cart"] = cart
    request.session.modified = True


def get_cart_items(request) -> Tuple[List[dict], Decimal, Decimal, Decimal, Decimal]:
    cart = get_cart(request.session)
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids, is_active=True).select_related("category").prefetch_related("gallery")

    items = []
    subtotal = Decimal("0.00")
    for product in products:
        data = cart.get(str(product.id), {})
        quantity = int(data.get("quantity", 1))
        price = product.price
        line_total = (price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        subtotal += line_total
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "price": price,
                "line_total": line_total,
            }
        )

    subtotal = subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if subtotal == Decimal("0.00"):
        shipping = Decimal("0.00")
        tax = Decimal("0.00")
    else:
        shipping = Decimal("0.00") if subtotal >= Decimal("200") else Decimal("9.00")
        tax = (subtotal * Decimal("0.09")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (subtotal + shipping + tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return items, subtotal, shipping, tax, total
