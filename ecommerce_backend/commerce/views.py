from rest_framework import viewsets, filters, status, generics, permissions as drf_permissions, exceptions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from .permissions import IsAdminUser, IsSellerOrReadOnly, IsOwner
from .filters import ProductFilter, CartFilter, OrderFilter, PaymentFilter
from .pagination import DefaultPagination
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Payment
from .serializers import (
    UserSerializer,
    CategorySerializer,
    ProductSerializer,
    CartItemSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PaymentSerializer,
)

# ---------------- Signup (Registration) ----------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [drf_permissions.AllowAny]

# ---------------- Users ----------------
class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsAdminUser]

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]

    def destroy(self, request, *args, **kwargs):
        if not getattr(request.user, "role", None) == "admin":
            raise exceptions.PermissionDenied("You do not have permission to delete users.")
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": f"User '{instance.username}' deleted successfully."},
            status=status.HTTP_200_OK
        )

# ---------------- Categories ----------------
class CategoryViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsSellerOrReadOnly]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = instance.name
        self.perform_destroy(instance)
        return Response(
            {"message": f"Category '{name}' deleted successfully"},
            status=status.HTTP_200_OK
        )

# ---------------- Products ----------------
class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsSellerOrReadOnly]
    pagination_class = DefaultPagination

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ["price", "created_at"]
    ordering = ["created_at"]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": f"Product '{instance.name}' deleted successfully"},
            status=status.HTTP_200_OK
        )

# ---------------- Cart ----------------
class CartViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = CartSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CartFilter
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Cart.objects.select_related("user").prefetch_related("items__product")
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": f"Cart {instance.cart_id} deleted successfully"},
            status=status.HTTP_200_OK
        )

# ---------------- Cart Items ----------------
class CartItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        user = self.request.user
        qs = CartItem.objects.select_related("cart", "product")
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(cart__user=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product_name = instance.product.name
        self.perform_destroy(instance)
        return Response(
            {"message": f"CartItem for '{product_name}' deleted successfully"},
            status=status.HTTP_200_OK
        )

# ---------------- Orders ----------------
class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ["ordered_date", "total_amount"]
    ordering = ["-ordered_date"]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related("user").prefetch_related("items__product")
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(user=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": f"Order {instance.id} deleted successfully"},
            status=status.HTTP_200_OK
        )

# ---------------- Order Items ----------------
class OrderItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [drf_permissions.IsAuthenticated, IsOwner]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        user = self.request.user
        qs = OrderItem.objects.select_related("order", "product")
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(order__user=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product_name = instance.product.name
        self.perform_destroy(instance)
        return Response(
            {"message": f"OrderItem for '{product_name}' deleted successfully"},
            status=status.HTTP_200_OK
        )

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
        user = self.request.user
        qs = Payment.objects.select_related("order__user")
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return qs.none()
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return qs
        return qs.filter(order__user=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        amount = instance.amount
        self.perform_destroy(instance)
        return Response(
            {"message": f"Payment of {amount} deleted successfully"},
            status=status.HTTP_200_OK
        )


def home(request):
    """Project Nexus Dashboard """
    data = {
        "app_name": "Project Nexus 🚀 - ProDev Backend",
        "status": "Running ✅",
        "description": "Elevate your backend skills and showcase your work with Project Nexus.",
        "developer": "Sewalew Setotaw",  
        "links": {
            "API Root": "/api/",
            "Swagger Docs": "/swagger/",
            "Redoc Docs": "/redoc/",
            "Admin Panel": "/admin/",
            "Obtain Token": "/api/token/",
            "Refresh Token": "/api/token/refresh/"
        }
    }

    # JSON fallback
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(data)

    # Generate cards for links
    cards_html = "".join(
        f"""
        <div class="card">
            <a href="{url}">{name}</a>
        </div>
        """ for name, url in data["links"].items()
    )

    # HTML dashboard
    html_content = f"""
    <html>
        <head>
            <title>{data['app_name']} Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0; padding: 0; background: #f4f6f8; color: #333;
                }}
                .header {{
                    background: #1a73e8; color: #fff;
                    text-align: center; padding: 40px 20px;
                }}
                .header h1 {{ margin: 0; font-size: 2.5rem; }}
                .header p {{ margin: 5px 0; font-size: 1.1rem; }}
                .header .developer {{ font-style: italic; margin-top: 10px; }}
                .container {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    max-width: 900px;
                    margin: 40px auto;
                    padding: 0 20px;
                }}
                .card {{
                    background: #fff;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    transition: transform 0.2s, box-shadow 0.2s;
                    text-align: center;
                }}
                .card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                }}
                .card a {{
                    text-decoration: none;
                    font-size: 1.2rem;
                    color: #1a73e8;
                    font-weight: 600;
                }}
                .card a:hover {{ text-decoration: underline; }}
                .footer {{
                    text-align: center; padding: 30px 20px; color: #555;
                    border-top: 1px solid #ddd;
                    margin-top: 40px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{data['app_name']}</h1>
                <p>{data['description']}</p>
                <p>Status: <strong>{data['status']}</strong></p>
                <p class="developer">Developed by: {data['developer']}</p>
            </div>

            <div class="container">
                {cards_html}
            </div>

            <div class="footer">
                &copy; 2025 All rights reserved.
            </div>
        </body>
    </html>
    """
    return HttpResponse(html_content)
