# commerce/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Payment


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="sewalew.setotaw",
            email="sewalews29@gmail.com",
            password="pass1234"
        )

    def test_user_registration(self):
        response = self.client.post("/api/auth/register/", {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass1234"
        })
        print("🔍 Users in DB after registration:", list(User.objects.values("username", "email")))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 2)

    def test_login(self):
        response = self.client.post("/api/auth/login/", {
            "username": "sewalew.setotaw",
            "password": "pass1234"
        })
        print("🔍 Login Response:", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)


class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="seller", password="pass1234", role="seller")
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Electronics")

    def test_create_product(self):
        response = self.client.post("/api/products/", {
            "name": "Laptop",
            "description": "Gaming Laptop",
            "price": "95000.00",
            "stock": 5,
            "category_id": str(self.category.category_id)
        })
        print("🔍 Products in DB:", list(Product.objects.values("name", "price", "stock")))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Laptop")


class CartTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="customer", password="pass1234")
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Books")
        self.product = Product.objects.create(
            name="Django for APIs",
            description="Book",
            price="5000.00",
            stock=10,
            category=self.category,
            seller=self.user
        )

    def test_add_to_cart(self):
        cart_response = self.client.post("/api/carts/")
        cart_id = cart_response.data["cart_id"]

        item_response = self.client.post("/api/cart-items/", {
            "cart_id": cart_id,
            "product_id": str(self.product.product_id),
            "quantity": 2
        })

        print("🔍 Carts in DB:", list(Cart.objects.values()))
        print("🔍 CartItems in DB:", list(CartItem.objects.values("cart_id", "product_id", "quantity")))
        self.assertEqual(cart_response.status_code, 201)
        self.assertEqual(item_response.status_code, 201)
        self.assertEqual(item_response.data["quantity"], 2)


class OrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="buyer", password="pass1234")
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Games")
        self.product = Product.objects.create(
            name="PlayStation 5",
            description="Gaming console",
            price="500.00",
            stock=3,
            category=self.category,
            seller=self.user
        )

    def test_create_order(self):
        order_response = self.client.post("/api/orders/", {}, format="json")
        print("🔍 Orders in DB:", list(Order.objects.values("user_id", "status", "total_amount")))
        self.assertEqual(order_response.status_code, 201)
        self.assertEqual(order_response.data["status"], "pending")
        self.assertEqual(order_response.data["total_amount"], "0.00")


class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="customer", password="pass1234")
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Tech")
        self.product = Product.objects.create(
            name="iPhone",
            description="Smartphone",
            price="999.00",
            stock=5,
            category=self.category,
            seller=self.user
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=999.00,
            status="pending"
        )
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=999.00)

    def test_create_payment(self):
        payment_response = self.client.post("/api/payments/", {
            "order_id": str(self.order.order_id),
            "amount": "999.00",
            "payment_method": "chapa",
            "status": "completed"
        })
        print("🔍 Payments in DB:", list(Payment.objects.values("order_id", "amount", "payment_method", "status")))
        self.assertEqual(payment_response.status_code, 201)
        self.assertEqual(payment_response.data["status"], "completed")
