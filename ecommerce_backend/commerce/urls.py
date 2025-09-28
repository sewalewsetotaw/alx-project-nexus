#category.urls

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from .views import (
    UserViewSet, 
    CategoryViewSet,
    ProductViewSet,
    CartViewSet,
    CartItemViewSet,
    RegisterView,
    OrderViewSet,
    OrderItemViewSet,
    PaymentViewSet
    )

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'carts', CartViewSet, basename='carts')
router.register(r'cart-items', CartItemViewSet, basename='cart-items')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'order-items', OrderItemViewSet, basename='order-items')
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    # Auth endpoints
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),        
    path("auth/logout/", TokenBlacklistView.as_view(), name="logout"),     

    # App routes
    path('', include(router.urls)),
]
