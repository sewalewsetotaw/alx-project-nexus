# category/serializers.py
from rest_framework import serializers
from .models import User,Category,Product

class UserSerializer(serializers.ModelSerializer):
   password = serializers.CharField(write_only=True)
   class Meta: 
        model=User
        fields=['user_id', 'username','first_name', 'last_name', 'email','phone_number', 'role', 'password','created_at']
        read_only_fields = ['user_id', 'created_at']
   
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
   
class CategorySerializer(serializers.ModelSerializer):
    products=serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'description', 'products']
        
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
