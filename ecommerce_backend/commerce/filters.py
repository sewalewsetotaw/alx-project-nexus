#commerce/filters.py

import django_filters
from .models import Product,Cart, Order, Payment


# ---------------- Product Filter ----------------
class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")  # case-insensitive partial match
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "name", "min_price", "max_price"]

# ---------------- Order Filter ----------------
class CartFilter(django_filters.FilterSet):
    created_min = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_max = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Cart
        fields = ["created_min", "created_max"]


# ---------------- Order Filter ----------------
class OrderFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    min_date = django_filters.DateFilter(field_name="ordered_date", lookup_expr="gte")
    max_date = django_filters.DateFilter(field_name="ordered_date", lookup_expr="lte")

    class Meta:
        model = Order
        fields = ["status", "min_date", "max_date"]


# ---------------- Payment Filter ----------------
class PaymentFilter(django_filters.FilterSet):
    payment_method = django_filters.CharFilter(field_name="payment_method", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    min_date = django_filters.DateFilter(field_name="payment_date", lookup_expr="gte")
    max_date = django_filters.DateFilter(field_name="payment_date", lookup_expr="lte")

    class Meta:
        model = Payment
        fields = ["payment_method", "status", "min_date", "max_date"]
