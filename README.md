# Events Platform Backend (Django + DRF)

A Role-Based Access Control (RBAC) backend for an events management platform. Built with Django and Django REST Framework, featuring custom email-based authentication and separate workflows for **Seekers** and **Facilitators**.

## 🚀 Features

* **Authentication:**
* Custom Login using Email (overriding Django's default Username requirement).
* Role selection at Signup (Seeker or Facilitator).
* Email OTP Verification (using Gmail SMTP).
* JWT Authentication (Access & Refresh tokens).


* **Facilitator Role:**
* Create, Update, Delete own events.
* View dashboard of created events.


* **Seeker Role:**
* Search events by location, language, and date.
* Enroll in events (with capacity checks).
* Prevent duplicate enrollments.


* **Tech Stack:** Django 4.0+, Django REST Framework, PostgreSQL, SimpleJWT.

---

## 🛠️ Setup & Installation

### 1. Prerequisites

* Python 3.8+
* PostgreSQL installed and running.

### 2. Clone & Environment

```bash
# Clone the repository
git clone <repository_url>
cd backend_task

# Create Virtual Environment
python -m venv venv

# Activate Virtual Environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Environment Variables

Create a `.env` file in the root directory and add the following configuration:

```env
# Database Configuration
DB_NAME=your_db_name
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Django Security
SECRET_KEY=your-secret-key-here
DEBUG=True

# Email Configuration (Gmail SMTP)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

```

### 5. Database Setup

Ensure your PostgreSQL server is running and the database defined in `DB_NAME` exists.

```bash
# Apply migrations to create tables
python manage.py makemigrations
python manage.py migrate

```

### 6. Run Server

```bash
python manage.py runserver

```

The API will be available at `http://127.0.0.1:8000/`.

---

## 🔌 API Endpoints

### Authentication

* `POST /auth/signup/` - Register as Seeker or Facilitator (triggers OTP).
* `POST /auth/verify-email/` - Verify account using OTP code.
* `POST /auth/login/` - Login with Email & Password (returns JWT).
* `POST /auth/refresh/` - Refresh expired access token.

### Events (Public/Seeker)

* `GET /events/search/` - List upcoming events.
* *Filters:* `?location=Online`, `?language=English`, `?starts_at__gte=2025-01-01`


* `POST /enrollments/` - Enroll in an event.
* `GET /enrollments/` - View my enrollments.

### Events (Facilitator)

* `GET /facilitator/events/` - List my created events.
* `POST /facilitator/events/` - Create a new event.
* `PUT /facilitator/events/{id}/` - Update an event.
* `DELETE /facilitator/events/{id}/` - Delete an event.

---

## 🧠 Design Decisions & Trade-offs

### 1. Custom Auth with Default User Model

* 
**Constraint:** The task required using Django's default `User` model but enforced Email-based login and no username in the request.


* **Decision:**
* We adhered to the constraint by **not** swapping the User model.
* **Workaround:** We generated a random unique `username` (UUID) in the background during signup to satisfy the database schema.
* **Login Logic:** implemented a custom `EmailTokenObtainPairSerializer` that looks up users by email, completely abstracting the `username` field from the client.



### 2. Role Management (Profile Model)

* **Decision:** Created a One-to-One `Profile` model to store the `role` (Seeker/Facilitator).
* **Reasoning:** Since we could not modify the `User` table directly, extending it via a related table is the standard Django pattern for adding attributes without breaking third-party apps (like Admin).

### 3. Synchronous Email Sending (Trade-off)

* **Current Implementation:** Emails are sent synchronously during the `signup` request using Django's `send_mail`.
* **Trade-off:** This blocks the HTTP request until the email provider responds, which can be slow.
* **Production Solution:** In a real production environment, this should be offloaded to a background task queue (like Celery + Redis) to ensure instant response times for the user.

### 4. Database Indexes

* **Decision:** Added `db_index=True` to `starts_at`, `location`, and `language` fields in the Event model.


* **Reasoning:** These are the primary filtering fields for Seekers. Indexing them ensures search queries remain fast as the dataset grows.