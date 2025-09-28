
from rest_framework import viewsets, filters, generics, permissions as drf_permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse, HttpResponse
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
