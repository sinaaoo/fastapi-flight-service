<<<<<<< HEAD
# Flights FastAPI (raw SQL, layered)

این پروژه یک مثال از پیاده‌سازی سرویس مدیریت پروازها با FastAPI است که:
- از ORM استفاده نمی‌کند (کوئری‌های مستقیم SQL با sqlite3)
- از معماری لایه‌ای استفاده می‌کند (routers → services → repositories → db)
- فشرده‌ترین امکانات: ایجاد، دریافت، فیلتر/صفحه‌بندی/مرتب‌سازی، ویرایش، حذف
- ثبت لاگ تغییرات در جدول `flight_logs`
- تست ساده با TestClient

## پیش‌نیازها
- Python 3.10+
- pip

## نصب و اجرا
1. clone یا کپی کردن این دایرکتوری
2. نصب وابستگی‌ها:
```bash
python -m venv .venv
source .venv/bin/activate   # یا Windows: .venv\Scripts\activate
pip install fastapi uvicorn pytest
=======
# fastapi-flight-service
>>>>>>> 1d893b749fc48064ea4b423c160d52eb5e8b09af
