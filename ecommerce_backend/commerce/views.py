from rest_framework import viewsets,filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Category, Product
from .serializers import UserSerializer, CategorySerializer, ProductSerializer

# ---------------- Users ----------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# ---------------- Categories ----------------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# ---------------- Products ----------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Filtering and Sorting
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category']  
    ordering_fields = ['price', 'created_at']  
    # ordering = ['price']  # default sort order