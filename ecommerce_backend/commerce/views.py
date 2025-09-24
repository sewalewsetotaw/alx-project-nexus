from rest_framework import viewsets, filters, generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User, Category, Product,Cart,CartItem,Order,OrderItem,Payment
from .serializers import UserSerializer, CategorySerializer, ProductSerializer,CartItemSerializer,CartSerializer,OrderSerializer,OrderItemSerializer,PaymentSerializer


# ---------------- Signup (Registration) ----------------
class RegisterView(generics.CreateAPIView):
    """
    Public endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # anyone can sign up


# ---------------- Users ----------------
class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]


# ---------------- Categories ----------------
class CategoryViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# ---------------- Products ----------------
class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Filtering and Sorting
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category']
    ordering_fields = ["price", "created_at"]
    ordering = ["created_at"]

    def perform_create(self, serializer):
        # Only sellers can add products
        if self.request.user.role != "seller":
            raise permissions.PermissionDenied("Only sellers can add products.")
        serializer.save(seller=self.request.user)


# ---------------- Cart ----------------
class CartViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        # Show only the logged-in user's carts
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------- Cart Items ----------------
class CartItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        # Show only items from the logged-in user's cart(s)
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart = serializer.validated_data["cart"]
        if cart.user != self.request.user:
            raise permissions.PermissionDenied("You can only add items to your own cart.")
        serializer.save()

# ---------------- Orders ----------------
class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------- Order Items ----------------
class OrderItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)


# ---------------- Payments ----------------
class PaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)