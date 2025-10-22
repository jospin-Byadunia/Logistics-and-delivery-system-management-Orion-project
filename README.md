# 🚛 Logistics and Delivery System Management

A modern **logistics and delivery management platform** built with **Python (Django & Django REST Framework)**.  
This project streamlines order creation, assignment, delivery tracking, and payment management between customers, drivers, and administrators.

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Core Models](#-core-models)
- [Business Logic](#-business-logic)
- [Installation & Setup](#-installation--setup)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Development Roadmap](#-development-roadmap)
- [Future Improvements](#-future-improvements)
- [License](#-license)
- [Author](#-author)

---

## 🌍 Overview

This system provides a digital solution for logistics operations by managing orders, driver assignments, and delivery lifecycles in a structured and transparent manner.  
It connects **customers**, **drivers**, and **administrators** through a unified backend system built on Django REST APIs.

The platform supports role-based permissions, dynamic order management, payments, and scalable delivery workflows.

---

## 🚀 Key Features

### 👤 Authentication & Roles
- Custom `User` model with email-based authentication  
- Role-based access control for:
  - **Admin** – manage users, orders, and payments  
  - **Customer** – create and track orders  
  - **Driver** – accept or reject delivery assignments  
- JWT-based authentication and token management  

### 📦 Order & Delivery Management
- Customers can create **delivery requests**
- Orders include pickup/drop-off details, distance, and pricing
- Drivers can **accept**, **reject**, or **complete** assigned deliveries
- Admins can **assign** or **reassign** deliveries manually

### 💳 Payment System
- Multiple payment methods:
  - **Card**
  - **Mobile Money**
  - **Pay on Delivery**
- Tracks order payments and integrates with delivery completion

### 🔄 Order Lifecycle

Every delivery order in the system follows a **clear and structured workflow** that ensures transparency, traceability, and accountability across all user roles (Customer, Driver, and Admin).

#### Workflow Stages:
1. **Pending** –  
   The order is created by the customer and awaits driver assignment or acceptance.

2. **Assigned** –  
   The admin manually assigns a driver, or the system automatically matches one based on availability.

3. **In Progress** –  
   The driver has accepted the order and is currently executing the delivery (e.g., en route to pickup or drop-off location).

4. **Completed** –  
   The delivery has been successfully completed and verified by the system. Payment status is updated accordingly.

5. **Rejected (Optional)** –  
   If a driver declines a delivery, the order returns to the pool or is reassigned to another driver by an admin.




---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend Framework** | Django 5.x, Django REST Framework |
| **Database** | MySQL / PostgreSQL |
| **Authentication** | JWT (SimpleJWT) |
| **Payments** | Card, Mobile Money, PayPal (future) |
| **Containerization** | Docker (optional for deployment) |
| **Version Control** | Git & GitHub |

---

## 📚 Core Models

### User
Custom user model extending `AbstractUser`, with email as the unique identifier.

### DeliveryRequest
Stores information about pickup/drop-off locations, customer, distance, computed price, and package type.

### Assignment
Tracks which driver is assigned to which delivery, and the assignment status:
- `ASSIGNED`
- `ACCEPTED`
- `REJECTED`
- `COMPLETED`

### Payment
Handles all payment records, method type, status, and linkage to deliveries.

---

## 🧾 API Endpoints (Sample)

Below is an overview of key API routes for the Logistics and Delivery System.  
All endpoints are prefixed with `/api/` and secured using **JWT authentication** where applicable.

---

### 🧍‍♂️ Authentication & User Management

| Endpoint | Method | Description | Access |
|-----------|--------|--------------|---------|
| `/api/auth/register/` | `POST` | Register a new user (Customer or Driver) | Public |
| `/api/auth/login/` | `POST` | Log in with email and password | Public |
| `/api/auth/logout/` | `POST` | Log out and blacklist JWT token | Authenticated |

---

### 📦 Orders & Deliveries

| Endpoint | Method | Description | Access |
|-----------|--------|-------------|---------|
| `/api/delivery-requests/` | `GET` | Retrieve all delivery-requests (filtered by role) | Authenticated |
| `/api/delivery-requests/` | `POST` | Create a new delivery order | Customer |
| `/api/delivery-requests/{id}/` | `GET` | Retrieve order details by ID | Authenticated |
| `/api/delivery-requests/{id}/update/` | `PATCH` | Update order details | Authenticated |
| `/api/delivery-requests/{id}/delete/` | `DELETE` | Delete an order | Admin |

#### 🔁 Order Lifecycle Actions
| Endpoint | Method | Description | Access |
|-----------|--------|-------------|---------|
| `/api/delivery-requests/{id}/assign/` | `POST` | Assign driver to an order | Admin |
| `/api/assignment/{id}/accept/` | `POST` | Driver accepts assigned order | Driver |
| `/api/assignment/{id}/reject/` | `POST` | Driver rejects order | Driver |
| `/api/assignment/{id}/complete/` | `PATCH` | Mark order as completed | Driver |

---

### 💳 Payments

| Endpoint | Method | Description | Access |
|-----------|--------|-------------|---------|
| `/api/payments/` | `POST` | Initiate a payment for an order | Customer |
| `/api/payments/{id}/` | `GET` | Retrieve payment details | Authenticated |
| `/api/payments/verify/` | `POST` | Verify payment transaction | System/Admin |
| `/api/payments/history/` | `GET` | Get all payments made by user | Authenticated |

---

### 🔐 Authentication Example (Headers)

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
Accept: application/json
```



## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/orion.git
cd orion
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 6. Configure Database

Create a MySQL or PostgreSQL database and update settings.py or .env accordingly.

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Start the Server
```bash
python manage.py runserver
```