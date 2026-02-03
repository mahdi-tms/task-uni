from decimal import Decimal
from shop.utils import get_cart_items


def cart_counts(request):
    cart_items, subtotal, shipping, tax, total = get_cart_items(request)
    return {
        "cart_count": sum(item['quantity'] for item in cart_items),
        "cart_subtotal": subtotal,
        "cart_total": total,
    }
