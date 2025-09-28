
from rest_framework import viewsets, filters, generics, permissions as drf_permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication

from .permissions import IsAdminUser, IsSellerOrReadOnly, IsOwner
from .filters import ProductFilter, CartFilter, OrderFilter, PaymentFilter
from .pagination import DefaultPagination
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Payment
from .serializers import (
    UserSerializer,
    CategorySerializer,
    ProductSerializer,
    # ProductListSerializer, ProductDetailSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PaymentSerializer,
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
    def destroy(self, request, *args, **kwargs):
        raise drf_permissions.PermissionDenied("Deleting users is not allowed.")

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
    # def get_serializer_class(self):
    #     if self.action == "list":
    #         return ProductListSerializer
    #     return ProductDetailSerializer
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


# ---------------- Cart ----------------
class CartViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated,IsOwner]
    serializer_class = CartSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CartFilter
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    def perform_create(self, serializer):
        # Auto assign logged-in user to cart
        serializer.save(user=self.request.user)
    def get_queryset(self):
        user = self.request.user
        qs = Cart.objects.select_related("user").prefetch_related("items__product")
        # Skip when swagger_fake_view or user not authenticated
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs  # admin sees all carts
        return qs.filter(user=user) 
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------- Cart Items ----------------
class CartItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        user=self.request.user
        qs=CartItem.objects.select_related("cart", "product")
        # Skip when swagger_fake_view or user not authenticated
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs  # admin sees all cart items
        return qs.filter(cart__user=user) 
        # return (
        #     CartItem.objects
        #     .filter(cart__user=self.request.user)
        #     .select_related("cart", "product")
        # )
    def perform_create(self, serializer):
        serializer.save()

# ---------------- Orders ----------------
class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = OrderSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ["ordered_date", "total_amount"]
    ordering = ["-ordered_date"]
    
    def perform_create(self, serializer):
        serializer.save()
    def get_queryset(self):
        user=self.request.user
        qs=Order.objects.select_related("user").prefetch_related("items__product")
        # Skip when swagger_fake_view or user not authenticated
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs  # admin sees all oders
        return qs.filter(user=user)


# ---------------- Order Items ----------------
class OrderItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        user=self.request.user
        qs=OrderItem.objects.select_related("order", "product")
        # Skip when swagger_fake_view or user not authenticated
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs  # admin sees all oders
        return qs.filter(order__user=user)
    
# ---------------- Payments ----------------
class PaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]

    def perform_create(self, serializer):

        order = serializer.validated_data["order"]
        serializer.save(order=order)

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related("order__user")
        # Skip when swagger_fake_view or user not authenticated
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(order__user=user)

   