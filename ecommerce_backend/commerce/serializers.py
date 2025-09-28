# category/serializers.py
from rest_framework import serializers
from .models import User,Category,Product,ProductImage,Cart,CartItem,Order,OrderItem,Payment
from django.contrib.auth.password_validation import validate_password

# ---------------- User ----------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta: 
        model = User
        fields = ['user_id', 'username', 'first_name', 'last_name', 'email',
                  'phone_number', 'password','role',  'created_at']
        read_only_fields = ['user_id','role', 'created_at']

    def validate_password(self, value):
        validate_password(value)   
        return value    
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if role and self.context['request'].user.role == 'admin':
            instance.role = role

        if password:
            instance.set_password(password)

        instance.save()
        return instance
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'description']

 # ---------------- Product Images ----------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]

 # ---------------- Product ----------------   
class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListSerializer(child=serializers.ImageField(), read_only=True)
    category_id = serializers.UUIDField()
    category = serializers.CharField(source="category.name", read_only=True)
    seller_id = serializers.UUIDField(source="seller.user_id", read_only=True)
    class Meta:
        model = Product
        fields = [
            "product_id", "name", "description", "price", "stock",
            "created_at", "updated_at",
            "seller_id","category_id", "category", "images"
        ]
        read_only_fields = ["product_id", "created_at", "updated_at", "seller_id", "category", "images"]

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

 # ---------------- CartItem ----------------
class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name", read_only=True)
    cart_id = serializers.UUIDField()
    product_id = serializers.UUIDField()

    class Meta:
        model = CartItem
        fields = ["cart_item_id", "cart_id", "product_id", "product", "quantity"]

    def create(self, validated_data):
        cart_id = validated_data.pop("cart_id")
        product_id = validated_data.pop("product_id")
        quantity = validated_data.pop("quantity", 1)

        # Get cart
        try:
            cart = Cart.objects.get(cart_id=cart_id)
        except Cart.DoesNotExist:
            raise serializers.ValidationError({"cart_id": "Invalid cart id."})

        # Get product
        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "Invalid product id."})

        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={"quantity": quantity}
        )

        if not created:
            # Update quantity instead of creating duplicate
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    
# ---------------- Cart ----------------
class CartSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user.user_id", read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['cart_id', 'user_id', 'created_at', 'items']
        read_only_fields = ['cart_id', 'created_at', 'user_id']

 # ---------------- OrderItem ----------------
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product.name", read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source="order",
        write_only=True
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'order_id', 'product_id', 'product', 'quantity', 'price']
        read_only_fields = ['order_item_id', 'product', 'price']

    def create(self, validated_data):
        # Price is automatically set from the product
        product = validated_data["product"]
        validated_data["price"] = product.price
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Only quantity is editable
        quantity = validated_data.get("quantity")
        if quantity is not None:
            instance.quantity = quantity
            instance.save()
        return instance


# ---------------- Order ----------------
class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user.user_id", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'user_id', 'total_amount', 'ordered_date', 'status', 'items']
        read_only_fields = ['order_id', 'ordered_date', 'user_id', 'total_amount']

    def create(self, validated_data):
        user = self.context['request'].user
        order = Order.objects.create(user=user, status='pending')
        cart = Cart.objects.filter(user=user).first()
        if cart and cart.items.exists():
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            cart.items.all().delete()
        return order
    
# ---------------- Payment ----------------
class PaymentSerializer(serializers.ModelSerializer):
    # order = OrderSerializer(read_only=True)
    # order_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Order.objects.all(), source="order", write_only=True
    # )
    # user = serializers.SerializerMethodField()
    order_id = serializers.UUIDField(write_only=True)
    order = serializers.CharField(source="order.order_id", read_only=True)
    user = serializers.CharField(source="order.user.username", read_only=True)
    class Meta:
        model = Payment
        fields = [
            'payment_id', 'order_id', 'order', 'user', 'amount',
            'payment_date', 'payment_method', 'status'
        ]
        read_only_fields = ['payment_id', 'payment_date']

    def get_user(self, obj):
        return obj.order.user.username
    def validate_amount(self, value):
        """
        Ensure payment amount does not exceed order total
        """
        order = self.initial_data.get("order_id")
        if order:
            order_instance = Order.objects.get(pk=order)
            if value > order_instance.total_amount:
                raise serializers.ValidationError("Payment cannot exceed order total amount")
        return value