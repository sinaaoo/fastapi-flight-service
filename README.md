


# ✈️ FastAPI Flight Management Service  
یک سرویس کامل مدیریت پرواز با FastAPI + SQLite (بدون ORM)

این پروژه یک **سرویس مدیریت پروازها**ست که با FastAPI و معماری لایه‌ای پیاده‌سازی شده و قابلیت‌های زیر را فراهم می‌کند:

- ایجاد پرواز جدید  
- دریافت لیست پروازها با:
  - Pagination  
  - Filtering  
  - Sorting  
- انتخاب ستون‌های دلخواه (Dynamic Field Projection)  
- ویرایش و حذف پرواز  
- ثبت لاگ تغییرات (Audit Log)  
- مدیریت وضعیت پرواز (Register Action)  
- استفاده از **Queryهای مستقیم SQL** بدون ORM  
- ساختار **Scalable + Clean Architecture**  
- تست نمونه برای یکی از Endpointها  
- هندلینگ کامل خطاهای HTTP و دیتابیس  

---

## 🚀 ویژگی‌های اصلی

### ✔ بدون ORM (تماماً Raw SQL Query)
برای افزایش کنترل و شفافیت در لایه دیتابیس از ORM استفاده نشده.

### ✔ معماری لایه‌ای (Layered Architecture)
پروژه شامل این لایه‌هاست:

app/
│── routers/        # مدیریت API endpoints
│── services/       # business logic
│── repositories/   # دسترسی به دیتابیس
│── models/         # مدل‌های Pydantic
│── db.py           # اتصال به SQLite
│── main.py         # ورودی اصلی FastAPI

### ✔ Dynamic Field Selection
مثال:

GET /flights?fields=origin,destination

### ✔ Pagination + Sorting + Filtering
مثال:

/flights?page=1&size=10&origin=THR&sort_by=departure_time&sort_order=desc

### ✔ ثبت لاگ تغییرات (Audit Log)
تمام تغییرات روی پرواز در جدول جداگانه ثبت می‌شود.

---

## 📦 نصب و اجرا

### 1. ایجاد محیط مجازی

python -m venv venv
source venv/bin/activate     # در ویندوز: venv\Scripts\activate

### 2. نصب وابستگی‌ها

pip install -r requirements.txt

### 3. ایجاد دیتابیس

python -c “from app.db import init_db; init_db()”

### 4. اجرای سرویس

uvicorn app.main:app –reload

API در این آدرس بالا می‌آید:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs

---

## 🧪 تست نمونه

pytest tests/test_flights.py

---

## 🔥 مثال درخواست‌ها

### ایجاد پرواز جدید

`POST /flights`

```json
{
  "flight_number": "IR-445",
  "origin": "THR",
  "destination": "MHD",
  "seats_total": 150,
  "seats_available": 70,
  "status": "scheduled"
}

نمایش فقط ستون‌های دلخواه

GET /flights?fields=origin,destination

ثبت تغییر وضعیت

POST /flights/1/register
{
  "changed_by": "admin",
  "new_status": "delayed",
  "note": "weather issue"
}




