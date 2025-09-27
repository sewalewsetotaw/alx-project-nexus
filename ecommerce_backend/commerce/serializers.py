# category/serializers.py
from rest_framework import serializers
from .models import User,Category,Product,ProductImage,Cart,CartItem,Order,OrderItem,Payment

# ---------------- User ----------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta: 
        model = User
        fields = ['user_id', 'username', 'first_name', 'last_name', 'email',
                  'phone_number', 'role', 'password', 'created_at']
        read_only_fields = ['user_id', 'created_at']

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


  # ---------------- Category ---------------- 
class CategorySerializer(serializers.ModelSerializer):
    products=serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'description', 'products']

 # ---------------- Product Images ----------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]

 # ---------------- Product ----------------   
class ProductSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Product
        fields = [
            "product_id", "name", "description", "price", "stock",
            "created_at", "updated_at",
            "seller", "category", "images", "category_id"
        ]
        read_only_fields = ["product_id", "created_at", "updated_at", "seller", "category", "images"]

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

 # ---------------- CartItem ----------------
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['cart_item_id', 'cart', 'product', 'product_id', 'quantity']

# ---------------- Cart ----------------
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['cart_id', 'user', 'created_at', 'items']
        read_only_fields = ['cart_id', 'created_at', 'user']

 # ---------------- Order Item ----------------
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'order', 'product', 'product_id', 'quantity', 'price']
        read_only_fields = ['order_item_id', 'price', 'product']

# ---------------- Order ----------------
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'user', 'total_amount', 'ordered_date', 'status', 'items']
        read_only_fields = ['order_id', 'ordered_date', 'user', 'total_amount']

    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     order = Order.objects.create(user=user)  # total_amount default=0
    #     return order
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
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source="order", write_only=True
    )
    user = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'payment_id', 'order', 'order_id', 'user', 'amount',
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