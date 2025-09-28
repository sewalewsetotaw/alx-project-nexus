# 🛒 E-Commerce Backend - ProDev BE

## 📌 Overview

This repository (`alx-project-nexus`) documents my learnings from the **ProDev Backend Engineering program**, presented through a **real-world case study**: building a backend for an **E-Commerce Platform**.

The backend is designed with **scalability, security, and performance** as top priorities. It demonstrates modern backend engineering practices, including:

- **RESTful APIs** for structured communication
- **JWT authentication & RBAC** for secure user management
- **Asynchronous task handling** with Celery + Redis
- **CI/CD pipelines** for automated testing & deployment
- **Containerized deployment** with Docker for environment consistency

---

## 🎯 Project Goals

- **CRUD APIs**: Manage products, categories, users, orders, and payments.
- **Filtering, Sorting & Pagination**: Efficient product discovery at scale.
- **Authentication & Authorization**: Secure access with JWT + role-based permissions.
- **Database Optimization**: Indexed queries for high-performance data retrieval.
- **Asynchronous Tasks**: Background processing (emails, order workflows, caching).
- **API Documentation**: Auto-generated Swagger/OpenAPI docs for developer integration.
- **Enterprise Practices**: CI/CD pipelines, containerization, secure headers, HTTPS/SSL.

---

## 🛠️ Technologies Used

| Technology                      | Purpose                                             |
| ------------------------------- | --------------------------------------------------- |
| **Django**                      | High-level backend framework for REST APIs          |
| **Django REST Framework (DRF)** | Toolkit for RESTful API development                 |
| **PostgreSQL**                  | Relational database with indexing and normalization |
| **JWT**                         | Authentication & role-based access control          |
| **Celery + Redis**              | Asynchronous tasks (emails, notifications, caching) |
| **Docker**                      | Containerization for consistent environments        |
| **Swagger/OpenAPI**             | Interactive API documentation and testing           |
| **CI/CD Pipelines**             | Automated testing & deployment (GitHub Actions)     |

---

## 🧩 Database Design

### 1. Users

- `user_id`, `full_name`, `username`, `email`, `password (hashed)`, `role`
- Roles: `customer`, `vendor`, `admin`
- Users can create carts, place orders,  and make payments.

### 2. Categories

- `category_id`, `name`, `description`, 

### 3. Products

- `product_id`, `name`, `description`, `price`, `stock`, `category_id`
- Linked to categories, supports inventory tracking.


### 4. Cart

- `cart_id`, `user_id`,  `created_at`
- Each cart contains multiple **Cart items**.

### 5. Cart Items

- `cart_item_id`, `cart_id`, `product_id`, `quantity`
### 6. Orders

- `order_id`, `user_id`, `total_amount`, `status`, `created_at`
- Each order contains multiple **order items**.

### 7. Order Items

- `order_item_id`, `order_id`, `product_id`, `quantity`, `price`

### 8. Payments

- `payment_id`, `order_id`, `user_id`, `amount`, `status`, `payment_date`


---

## 🔑 Key Features

### 1. CRUD Operations

- Products → `/api/products/`
- Categories → `/api/categories/`
- Cart & Items → `/api/carts/`
- Orders & Items → `/api/orders/`
- Users & Auth → `/api/auth/register`, `/api/auth/login` (JWT)

### 2. REST API Query Features

- **Filtering** → `/api/products/?category=electronics&price_min=100&price_max=1000`
- **Sorting** → `/api/products/?ordering=price` or `/api/products/?ordering=-created_at`
- **Pagination** → `/api/products/?page=2&page_size=20`

### 3. Asynchronous Processing

- **Celery + Redis** handles:
  - Order confirmation emails
  - Payment reconciliation
  - Caching heavy queries

### 4. API Documentation

- Swagger UI → `/api/docs/`
- Postman collections supported

---

## 🔒 API Security

1. **JWT Authentication** – Token-based secure sessions
2. **Role-based Access Control (RBAC)** – Permissions for `customer`, `vendor`, `admin`
3. **Input Validation** – Strict data validation with DRF serializers

---

## 🔁 CI/CD Pipeline

- **CI** → Automated tests (unit + integration) run on pull requests
- **CD** → Staging & production deployments
- **Dockerized services** → PostgreSQL, Redis, Django API for portability

---

## 🚀 Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/sewalewsetotaw/alx-project-nexus.git
cd alx-project-nexus
```
