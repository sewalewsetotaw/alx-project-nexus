from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F, Sum
from .models import OrderItem, Order, Product

# ---------------- Update Order total_amount ----------------
@receiver(post_save, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    order = instance.order
    total = order.items.aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0
    order.total_amount = total
    order.save()

# ---------------- Update Product stock when order confirmed ----------------
@receiver(post_save, sender=OrderItem)
def reduce_stock(sender, instance, created, **kwargs):
    if created and instance.order.status == 'confirmed':
        product = instance.product
        if product.stock >= instance.quantity:
            product.stock -= instance.quantity
            product.save()
