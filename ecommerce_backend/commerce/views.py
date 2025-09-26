from rest_framework import viewsets, filters, generics
from rest_framework import permissions as drf_permissions
from .permissions import IsAdminUser, IsSellerOrReadOnly, IsOwner

from .filters import ProductFilter, OrderFilter, PaymentFilter
from .pagination import DefaultPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User, Category, Product,Cart,CartItem,Order,OrderItem,Payment
from .serializers import (
    UserSerializer,
    CategorySerializer,
    ProductSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PaymentSerializer
)


# ---------------- Signup (Registration) ----------------
class RegisterView(generics.CreateAPIView):
    """
    Public endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [drf_permissions.AllowAny]  # anyone can sign up


# ---------------- Users ----------------
class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated,IsAdminUser]

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]


# ---------------- Categories ----------------
class CategoryViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsSellerOrReadOnly]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# ---------------- Products ----------------
class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsSellerOrReadOnly]
    pagination_class=DefaultPagination
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ["price", "created_at"]
    ordering = ["created_at"]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


# ---------------- Cart ----------------
class CartViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated]
    serializer_class = CartSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ["ordered_date", "total_amount"]
    ordering = ["-ordered_date"]


    def get_queryset(self):
        # Show only the logged-in user's carts
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------- Cart Items ----------------
class CartItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        # Show only items from the logged-in user's cart(s)
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart = serializer.validated_data["cart"]
        if cart.user != self.request.user:
            raise drf_permissions.PermissionDenied("You can only add items to your own cart.")
        serializer.save()

# ---------------- Orders ----------------
class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------- Order Items ----------------
class OrderItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)


# ---------------- Payments ----------------
class PaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)