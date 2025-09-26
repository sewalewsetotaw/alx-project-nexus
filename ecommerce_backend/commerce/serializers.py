# category/serializers.py
from rest_framework import serializers
from .models import User,Category,Product,Cart,CartItem,Order,OrderItem,Payment

# ---------------- User ----------------
class UserSerializer(serializers.ModelSerializer):
   password = serializers.CharField(write_only=True)
   class Meta: 
        model=User
        fields=['user_id', 'username','first_name', 'last_name', 'email','phone_number', 'role', 'password','created_at']
        read_only_fields = ['user_id','role', 'created_at']
   
   def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
   
   def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
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
 # ---------------- Product ----------------       
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    seller = UserSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='seller', write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'product_id', 'name', 'description', 'price', 'stock',
            'created_at', 'updated_at',
            'category', 'category_id', 'seller', 'seller_id'
        ]

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
        read_only_fields = ['cart_id', 'created_at']

 # ---------------- Order Item ----------------
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['order_item_id', 'order', 'product', 'product_id', 'quantity', 'price']


# ---------------- Order ----------------
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'user', 'total_amount', 'ordered_date', 'status', 'items']
        read_only_fields = ['order_id', 'ordered_date']


# ---------------- Payment ----------------
class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source="order", write_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'payment_id', 'order', 'order_id', 'user', 'amount',
            'payment_date', 'payment_method', 'status'
        ]
        read_only_fields = ['payment_id', 'payment_date']       