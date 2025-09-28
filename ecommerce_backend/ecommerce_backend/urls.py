from django.contrib import admin
from django.http import JsonResponse
from django.urls import include,path
from rest_framework_simplejwt import views as jwt_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi 
from django.conf import settings
from django.conf.urls.static import static
from commerce.views import home 

schema_view = get_schema_view(
    openapi.Info(
        title="Project Nexus API 🚀 - ProDev Backend",
        default_version='v1.0.0',
        description="""
        Welcome to **Project Nexus API Documentation**!

        Project Nexus is part of the ProDev Backend Program, showcasing a professional e-commerce backend built with Django REST Framework.  

        **Hosted Project:** [Live Demo](https://ecommerce-backend-ur2g.onrender.com)  
        **GitHub Repository:** [View Code](https://github.com/sewalewsetotaw)  
        **Developer Contact:** sewalews29@gmail.com  

        **Key Features:**
        - User Authentication & JWT Tokens
        - Products & Categories Management
        - Cart, Orders, and Payments
        - Admin Panel & Developer Tools
        - Fully documented REST API with Swagger & Redoc
        - Designed for scalability and professional standards

        **Developer:** Sewalew Setotaw  
        **Status:** Production-Ready 🚀

        **Usage Notes:**
        - All endpoints require JWT authentication unless marked as public
        - Use the `/api/token/` endpoint to obtain your token
        - Pagination and filtering are available on most endpoints
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="sewalews29@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],  
)

urlpatterns = [
    path("", home, name="home"),  # root path
    path('api/token/',
         jwt_views.TokenObtainPairView.as_view(),
         name ='token_obtain_pair'),
    path('api/token/refresh/',
         jwt_views.TokenRefreshView.as_view(),
         name ='token_refresh'),
    path('admin/', admin.site.urls),
    path('api/', include('commerce.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)