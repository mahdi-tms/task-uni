from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, RegisterForm, LoginForm
from .models import Category, Product, Order, OrderItem
from .utils import get_cart, save_cart, get_cart_items


def home(request):
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_active=True).order_by("-created_at")[:8]
    best_sellers = Product.objects.filter(is_active=True).order_by("price")[:8]
    return render(
        request,
        "shop/home.html",
        {
            "categories": categories,
            "featured_products": featured_products,
            "best_sellers": best_sellers,
        },
    )


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.all()

    query = request.GET.get("q", "")
    category_slug = request.GET.get("category", "")
    sort = request.GET.get("sort", "")

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)

    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "shop/product_list.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "query": query,
            "category_slug": category_slug,
            "sort": sort,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("gallery"),
        slug=slug,
        is_active=True,
    )
    related = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(id=product.id)
        .order_by("-created_at")[:4]
    )
    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
            "related": related,
        },
    )


@require_POST
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))
    product = get_object_or_404(Product, id=product_id, is_active=True)

    cart = get_cart(request.session)
    current_qty = cart.get(str(product.id), {}).get("quantity", 0)
    cart[str(product.id)] = {"quantity": current_qty + max(quantity, 1)}
    save_cart(request, cart)

    messages.success(request, f"«{product.name}» به سبد خرید افزوده شد.")
    return redirect(request.META.get("HTTP_REFERER", product.get_absolute_url()))


@require_POST
def update_cart(request):
    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))
    cart = get_cart(request.session)

    if product_id in cart:
        if quantity <= 0:
            cart.pop(product_id)
            messages.info(request, "محصول از سبد حذف شد.")
        else:
            cart[product_id]["quantity"] = quantity
            messages.success(request, "تعداد به‌روزرسانی شد.")
        save_cart(request, cart)
    return redirect("shop:cart")


@require_POST
def remove_from_cart(request):
    product_id = request.POST.get("product_id")
    cart = get_cart(request.session)
    if product_id in cart:
        cart.pop(product_id)
        save_cart(request, cart)
        messages.info(request, "محصول حذف شد.")
    return redirect("shop:cart")


def cart_view(request):
    items, subtotal, shipping, tax, total = get_cart_items(request)
    return render(
        request,
        "shop/cart.html",
        {"items": items, "subtotal": subtotal, "shipping": shipping, "tax": tax, "total": total},
    )


@login_required
def checkout(request):
    items, subtotal, shipping, tax, total = get_cart_items(request)
    if not items:
        messages.warning(request, "سبد خرید شما خالی است.")
        return redirect("shop:product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order: Order = form.save(commit=False)
            order.user = request.user
            order.subtotal = subtotal
            order.shipping = shipping
            order.tax = tax
            order.total = total
            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    name=item["product"].name,
                    price=item["price"],
                    quantity=item["quantity"],
                )

            request.session["cart"] = {}
            messages.success(request, "سفارش شما ثبت شد.")
            return redirect("shop:checkout_success", order_id=order.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            full_name = f"{request.user.first_name} {request.user.last_name}".strip()
            initial = {"full_name": full_name, "email": request.user.email}
        form = CheckoutForm(initial=initial)

    return render(
        request,
        "shop/checkout.html",
        {
            "form": form,
            "items": items,
            "subtotal": subtotal,
            "shipping": shipping,
            "tax": tax,
            "total": total,
        },
    )


@login_required
def checkout_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "shop/checkout_success.html", {"order": order})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "خوش آمدید! حساب شما ساخته شد.")
            return redirect("/")
    else:
        form = RegisterForm()
    return render(request, "shop/auth/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    next_url = request.GET.get("next") or request.POST.get("next")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        remember = request.POST.get("remember_me") == "on"
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session.set_expiry(1209600 if remember else 0)
            messages.success(request, "با موفقیت وارد شدید.")
            return redirect(next_url or "/")
    else:
        form = LoginForm(request)

    return render(request, "shop/auth/login.html", {"form": form, "next": next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "خروج با موفقیت انجام شد.")
    return redirect("/")

# Create your views here.
