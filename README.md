# workforce-api
Simple workforce management backend API built with Django REST Framework. Handles authentication, bookings, and basic worker management.


# Ideal Gilam — Backend API

Gilam yuvish xizmati uchun yozilgan backend tizimi.

## Texnologiyalar
- **Python 3.14** + **Django 6.0**
- **Django REST Framework** — API
- **PostgreSQL** — Ma'lumotlar bazasi
- **JWT (SimpleJWT)** — Autentifikatsiya
- **drf-spectacular** — Swagger dokumentatsiya
- **django-cors-headers** — CORS

---

## O'rnatish

### 1. Virtual muhit
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

### 2. `.env` fayl yarating
```env
SECRET_KEY=yangi-secret-key-yozing
DEBUG=True
DB_NAME=ideal_gilam
DB_USER=postgres
DB_PASSWORD=sizning_parolingiz
DB_HOST=localhost
DB_PORT=5432
```

### 3. Database yarating
```sql
CREATE DATABASE ideal_gilam;
```

### 4. Migratsiya
```bash
python manage.py migrate
```

### 5. Superuser yarating
```bash
python manage.py createsuperuser
```

### 6. Serverni ishga tushiring
```bash
python manage.py runserver
```

### 7. Swagger dokumentatsiya
```
http://127.0.0.1:8000/
```

---

## API Endpointlar

### 🔐 Autentifikatsiya

#### `POST /login/`
Tizimga kirish. Token olish.

**So'rov:**
```json
{
  "username": "admin",
  "password": "123456"
}
```
**Javob:**
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "role": "admin",
  "username": "admin",
  "first_name": "Ali",
  "last_name": "Valiyev"
}
```

#### `POST /token/refresh/`
Access tokenni yangilash.
```json
{ "refresh": "eyJ..." }
```

---

### 👤 Profil

#### `GET /me/`
Login bo'lgan foydalanuvchining profilini ko'rish.

**Javob:**
```json
{
  "id": 1,
  "username": "admin",
  "first_name": "Ali",
  "last_name": "Valiyev",
  "number": "+998901234567",
  "living_address": "Tashkent",
  "work_type": "yuvuvchi",
  "role": "admin"
}
```

#### `PATCH /me/`
Profilni tahrirlash (username va role o'zgarmaydi).
```json
{
  "first_name": "Yangi ism",
  "last_name": "Yangi familiya",
  "number": "+998901234567",
  "living_address": "Andijon"
}
```

---

### 👷 Ishchilar (faqat Admin)

#### `GET /admin-dashboard/users`
Barcha ishchilar ro'yxati.

**Javob:**
```json
[
  {
    "id": 1,
    "username": "worker1",
    "first_name": "Ali",
    "last_name": "Valiyev",
    "number": "+998901234567",
    "living_address": "Tashkent",
    "work_type": "yuvuvchi",
    "percentage_work": 30.0,
    "work_day": "Du-Ju",
    "rest_day": "Sha-Ya",
    "role": "worker"
  }
]
```

#### `POST /admin-dashboard/create-user`
Yangi ishchi qo'shish.
```json
{
  "username": "worker2",
  "password": "xavfsiz_parol",
  "first_name": "Hasan",
  "last_name": "Karimov",
  "number": "+998901234567",
  "living_address": "Andijon",
  "work_type": "yuvuvchi",
  "percentage_work": 30,
  "work_day": "Du-Ju",
  "rest_day": "Sha-Ya",
  "role": "worker"
}
```

> `work_type` qiymatlari: `yuvuvchi` yoki `yetkazuvchi`
> `role` qiymatlari: `worker` yoki `admin`

#### `GET /admin-dashboard/users/{id}/`
Bitta ishchi ma'lumoti.

#### `PATCH /admin-dashboard/users/{id}/`
Ishchini tahrirlash.

#### `DELETE /admin-dashboard/users/{id}/`
Ishchini o'chirish.

---

### 📦 Zakazlar

#### Admin endpointlar

##### `GET /admin-dashboard/orders`
Barcha zakazlar ro'yxati.

**Query parametrlar:**
- `?status=washing` — Yuvilayotganlar
- `?status=bringing` — Yetkazilayotganlar
- `?status=delivered` — Yetkazilganlar

**Javob:**
```json
[
  {
    "id": 1,
    "name": "Hamid Karimov",
    "number": "+998901234567",
    "address": "Tashkent",
    "date": "2025-11-01",
    "type": {"id": 1, "name": "Gilam"},
    "width": 3.0,
    "height": 4.0,
    "kg": null,
    "price": "250000.00",
    "status": "washing",
    "worker": 2,
    "worker_name": "Ali Valiyev",
    "created_at": "2025-11-01T10:00:00Z"
  }
]
```

##### `POST /admin-dashboard/orders`
Admin zakaz qo'shish.
```json
{
  "name": "Mijoz ismi",
  "number": "+998901234567",
  "address": "Manzil",
  "date": "2025-11-01",
  "type_name": "Gilam",
  "width": 3.0,
  "height": 4.0,
  "kg": null,
  "price": 250000,
  "status": "washing",
  "izox": "Izoh"
}
```

##### `GET /admin-dashboard/orders/{id}/`
Bitta zakaz tafsiloti.

##### `PATCH /admin-dashboard/orders/{id}/`
Zakazni tahrirlash (status, narx va boshqalar).

##### `DELETE /admin-dashboard/orders/{id}/`
Zakazni o'chirish.

##### `GET /admin-dashboard/stats`
Dashboard statistika.

**Javob:**
```json
{
  "total_orders": 150,
  "today_orders": 5,
  "month_orders": 45,
  "total_revenue": "7500000.00",
  "month_revenue": "2250000.00",
  "by_status": [
    {"status": "washing", "count": 20},
    {"status": "bringing", "count": 15},
    {"status": "delivered", "count": 110}
  ]
}
```

#### Worker endpointlar

##### `GET /worker/orders/`
Worker o'zining zakazlarini ko'radi.

##### `POST /worker/orders/add/`
Worker yangi zakaz qo'shadi.
```json
{
  "name": "Mijoz ismi",
  "number": "+998901234567",
  "address": "Manzil",
  "date": "2025-11-01",
  "type_name": "Ko'rpa",
  "width": null,
  "height": null,
  "kg": 3.5,
  "price": 150000,
  "status": "washing",
  "izox": ""
}
```

##### `PATCH /worker/orders/{id}/status/`
Worker zakazning statusini o'zgartiradi.
```json
{ "status": "bringing" }
```

**Status qiymatlari:**
| Qiymat | Ma'nosi |
|--------|---------|
| `washing` | Yuvilmoqda |
| `bringing` | Yetkazilmoqda |
| `delivered` | Yetkazildi |

---

### 📅 Davomat (faqat Admin)

#### `GET /admin-dashboard/attendance/`
Barcha davomat yozuvlari.

**Query parametr:**
- `?week_start=2025-11-03` — Hafta boshidan filtr

**Javob:**
```json
[
  {
    "id": 1,
    "worker": 2,
    "worker_name": "Ali Valiyev",
    "date": "2025-11-03",
    "status": "present"
  }
]
```

#### `POST /admin-dashboard/attendance/mark/`
Bitta kun davomati belgilash.
```json
{
  "worker": 2,
  "date": "2025-11-03",
  "status": "present"
}
```
> `status` qiymatlari: `present` (keldi) yoki `absent` (kelmadi)

#### `POST /admin-dashboard/attendance/bulk/`
Bir nechta davomat birdan saqlash.
```json
{
  "records": [
    {"worker": 1, "date": "2025-11-03", "status": "present"},
    {"worker": 2, "date": "2025-11-03", "status": "absent"},
    {"worker": 3, "date": "2025-11-03", "status": "present"}
  ]
}
```

---

### 📋 Zakaz turlari

#### `GET /order-types/`
Barcha zakaz turlari ro'yxati (Gilam, Parda, Ko'rpa, Yostiq).

#### `POST /order-types/`
Yangi tur qo'shish.
```json
{ "name": "Kigiz" }
```

---

## Xavfsizlik

Barcha endpointlar (login dan tashqari) JWT token talab qiladi:
```
Authorization: Bearer <access_token>
```

**Rollar:**
- `admin` — hamma endpointlarga kirish huquqi
- `worker` — faqat o'z zakazlari va profili

---

## Testlar

```bash
python manage.py test
```

Jami **36 ta test** — hammasi o'tishi kerak:
```
Ran 36 tests in ~50s
OK
```

---

## Loyiha strukturasi

```
ideal_gilam/
├── config/
│   ├── settings.py      # Asosiy sozlamalar
│   └── urls.py          # Bosh URL
├── users/               # Ishchilar + Auth
│   ├── models.py        # Worker modeli
│   ├── serializers.py   # Ma'lumot formatlash
│   ├── views.py         # API logika
│   └── urls.py          # URL yo'llari
├── orders/              # Zakazlar
│   ├── models.py        # Order, OrderType modeli
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── attendance/          # Davomat
│   ├── models.py        # Attendance modeli
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── .env                 # Maxfiy sozlamalar (git ga yuklanmaydi)
├── requirements.txt     # Kerakli paketlar
└── manage.py
```

---

## Muallif
Backend: Django REST Framework
Swagger: http://127.0.0.1:8000/