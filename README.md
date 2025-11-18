# 🚛 Logistics and Delivery System Management

A modern **logistics and delivery management platform** built with **Python (Django & Django REST Framework)**.  
This project streamlines order creation, assignment, delivery tracking, and payment management between customers, drivers, and administrators.

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend Framework** | Django 5.x, Django REST Framework |
| **Database** | MySQL / PostgreSQL |
| **Authentication** | JWT (SimpleJWT) |
| **Payments** | Card, Mobile Money, PayPal (future) |
| **Version Control** | Git & GitHub |

---
## Project structure
```bash
delivery-management-api/
│
├── manage.py
├── requirements.txt
├── .env
├── README.md
│
├── OrionProject/                 # Main project configuration (settings, urls, wsgi)
│
├── api/
│   ├── utils/             
│   ├── views              
│   ├── serializers        
│   ├── models             
│   └── urls               
```


## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/jospin-Byadunia/Logistics-and-delivery-system-management-Orion-project.git
cd Logistics-and-delivery-system-management-Orion-project
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

Example of .env
```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/orion_db
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=your_project_db
DB_USER=your_DB_user
DB_PASSWORD=your_password
DB_PORT=3306

```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Start the Server
```bash
python manage.py runserver
```
### 7. Authentication (JWT)

To obtain tokens:
```bash
POST /api/token/
{
  "username": "your_username",
  "password": "your_password"
}
```

Use in headers:
```bash
Authorization: Bearer <access_token>
```

Refresh token:
```bash
POST /api/token/refresh/
{
  "refresh": "<refresh_token>"
}
```

🧾 License

MIT License © 2025 Jospin
