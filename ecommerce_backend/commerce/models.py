# category/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, CheckConstraint
import uuid
from phonenumber_field.modelfields import PhoneNumberField
# ---------------- User ----------------   
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    ]
    user_id  = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False,
                            db_index=True)
    email  =models.EmailField(unique=True,null=False)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone_number = PhoneNumberField(region="ET",blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

# ---------------- Category ----------------   

class Category(models.Model):
    category_id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125,unique=True)
    description = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.name

# ---------------- Product ----------------   
class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200,null=False,blank=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            CheckConstraint(check=Q(stock__gte=0), name='stock_non_negative'),
        ]

    def __str__(self):
        return self.name

# ---------------- Product Images ----------------
class ProductImage(models.Model):
    image_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_images/")  # MEDIA_ROOT/product_images/

    def __str__(self):
        return f"Image for {self.product.name}"
    
# ---------------- Cart ----------------
class Cart(models.Model):
    cart_id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.cart_id)

# ---------------- CartItem ----------------
class CartItem(models.Model):
    cart_item_id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity=models.PositiveIntegerField()
    class Meta:
        unique_together = ('cart', 'product'),
        constraints = [
            CheckConstraint(check=Q(quantity__gt=0), name='cartitem_quantity_positive'),
            models.UniqueConstraint(fields=['cart','product'], name='unique_cart_product'),
        ]

    def __str__(self):
        return f"{self.product.name}  ({self.quantity})"

# ---------------- Order ----------------
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)    
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    def __str__(self):
        return f"Order {self.order_id} - {self.user.username} ({self.status})"

# ---------------- OrderItem ----------------
class OrderItem(models.Model):
    order_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

# ---------------- Payment ----------------
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('chapa', 'Chapa'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    @property
    def user(self):
        return self.order.user
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"


