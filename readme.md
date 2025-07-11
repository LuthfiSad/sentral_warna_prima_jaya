# Face Recognition API

Face Recognition API adalah aplikasi berbasis FastAPI yang menyediakan fitur pendaftaran dan verifikasi wajah menggunakan JWT authentication.

## Teknologi yang Digunakan

Aplikasi ini dibangun menggunakan:
- **FastAPI** - Framework web modern berbasis Python.
- **Pydantic** - Validasi data.
- **SQLAlchemy** - ORM untuk database.
- **JWT (JSON Web Token)** - Autentikasi dan otorisasi.
- **Alembic** - Migrasi database.
- **Uvicorn** - Server ASGI untuk menjalankan aplikasi.
- **MapboxGL** - Untuk tampilan peta jika diperlukan.
- **Material Tailwind React** - Untuk tampilan UI jika digunakan dalam frontend.

## Instalasi dan Menjalankan Aplikasi

### 1. Clone Repository
```sh
git clone https://github.com/{username}/face-id-detector-python.git
cd face-id-detector-python
```

### 2. Buat Virtual Environment
```sh
python -m venv env
source env/bin/activate  # MacOS/Linux
env\Scripts\activate  # Windows
```

### 3. Instalasi Dependencies
```sh
pip install -r requirements.txt
```

### 4. Konfigurasi Database
Sesuaikan konfigurasi database di `src/config/settings.py`.

### 5. Jalankan Migrasi Database
```sh
alembic upgrade head
```

### 6. Menjalankan Server
```sh
python -m src.main
```
atau
```sh
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

## Endpoint API

### 1. Autentikasi
- **POST /auth/login** → Login untuk mendapatkan token JWT.
- **POST /auth/register** → Registrasi pengguna baru.

### 2. Face Recognition
- **POST /face/register** → Mendaftarkan wajah pengguna dengan JWT authentication.
- **POST /face/verify** → Verifikasi wajah pengguna dengan JWT authentication.

### 3. Restricted Access
- **POST /restricted** → Endpoint yang hanya dapat diakses oleh user dengan username.

## Struktur Direktori
```
/face-id-detector-python
 ├── src/
 │   ├── config/             # Konfigurasi database & environment
 │   ├── routes/             # Routing layer
 │   ├── controllers/        # Controller layer
 │   ├── services/           # Business logic layer
 │   ├── models/             # Data models (Schemas & ORM)
 │   ├── schemas/            # Request & Response Schemas
 │   ├── middlewares/        # Middleware (Auth, Logging, etc.)
 │   ├── utils/              # Helper functions
 │   ├── main.py             # Entry point
 ├── .env                    # Environment variables
 ├── requirements.txt
 ├── alembic/                # Database migrations
 └── ...

```

## workflow
# 🚀 Vehicle Repair Management System - Flow Documentation

## Overview
Sistem manajemen perbaikan kendaraan dengan flow yang terstruktur dari pendaftaran customer hingga pembayaran.

## 🔄 Complete Flow

### 1️⃣ Customer Datang & Serah Mobil
**Endpoint:** `POST /api/customers/`
```json
{
  "name": "John Doe",
  "address": "Jl. Merdeka No. 123",
  "phone": "081234567890",
  "email": "john@email.com",
  "plate_number": "B1234ABC",
  "vehicle_type": "Toyota Avanza",
  "vehicle_model": "2020",
  "vehicle_year": "2020"
}
```

**Scan Plat Nomor (Customer Lama):**
`GET /api/customers/search/plate/B1234ABC`

### 2️⃣ Admin Buat Transaksi Perbaikan
**Endpoint:** `POST /api/transactions/`
```json
{
  "customer_id": 1,
  "complaint": "Mesin bermasalah, suara kasar saat idle"
}
```

**Response:** Status otomatis `PENDING`

### 3️⃣ Karyawan Mulai Pengerjaan
**Auto-trigger saat buat laporan pertama atau manual:**
`POST /api/transactions/{transaction_id}/start-work`

**Status berubah:** `PENDING` → `PROSES`

### 4️⃣ Karyawan Buat Draft Laporan
**Endpoint:** `POST /api/reports/`
```json
{
  "transaction_id": 1,
  "description": "Ganti oli mesin dan filter oli",
  "start_time": "2025-01-10T08:00:00",
  "end_time": "2025-01-10T09:30:00"
}
```

**Status:** `DRAFT` (bisa diedit berkali-kali)

### 5️⃣ Submit Laporan untuk Approval
**Endpoint:** `POST /api/reports/{report_id}/submit`

**Status berubah:**
- Report: `DRAFT` → `APPROVED`
- Transaction: `PROSES` → `MENUNGGU_APPROVAL`

### 6️⃣ Admin/Supervisor Approval
**Approve:** `POST /api/reports/{report_id}/approve`
```json
// Response: status = "APPROVED"
```

**Reject:** `POST /api/reports/{report_id}/reject`
```json
{
  "reason": "Deskripsi kurang detail, tambahkan foto before/after"
}
```

**Status jika reject:** `APPROVED` → `REJECTED` (karyawan bisa edit ulang)

### 7️⃣ Admin Update Biaya & Finalisasi
**Calculate Total Cost:** `POST /api/transactions/{transaction_id}/calculate-cost`

**Finalize Transaction:** `POST /api/transactions/{transaction_id}/finalize`

**Status berubah:** `MENUNGGU_APPROVAL` → `SELESAI`

### 8️⃣ Customer Bayar & Ambil Mobil
**Mark as Paid:** `POST /api/transactions/{transaction_id}/mark-paid`

**Status berubah:** `SELESAI` → `DIBAYAR`

## 📋 Status Flow Chart

```
CUSTOMER REGISTRATION
         ↓
   CREATE TRANSACTION (PENDING)
         ↓
   START WORK (PROSES)
         ↓
   CREATE DRAFT REPORTS
         ↓
   SUBMIT REPORTS (MENUNGGU_APPROVAL)
         ↓
   ADMIN APPROVAL/REJECTION
         ↓
   CALCULATE COST & FINALIZE (SELESAI)
         ↓
   MARK AS PAID (DIBAYAR)
```

## 🎯 Key Features

### Customer Management
- ✅ Scan plat nomor untuk customer lama
- ✅ Auto-load data customer & kendaraan
- ✅ Registrasi customer baru sekali saja

### Transaction Workflow
- ✅ Admin pilih customer → auto tampil data mobil
- ✅ Auto status progression
- ✅ History tracking setiap perubahan status

### Report System
- ✅ Karyawan buat draft laporan per pekerjaan
- ✅ Submit untuk approval
- ✅ Admin approve/reject dengan alasan
- ✅ Edit laporan yang di-reject
- ✅ Upload foto before/after

### Permission & Security
- ✅ Karyawan hanya lihat/edit laporan sendiri
- ✅ Admin bisa approve/reject semua laporan
- ✅ Role-based access control

## 📱 Mobile App Support
Semua endpoint support untuk mobile app dengan:
- File upload untuk foto
- Form data untuk input yang mudah
- JWT authentication
- Offline-first dengan sync capability

## 🔍 API Endpoints Summary

### Customer Endpoints
```
POST   /api/customers/                    # Create new customer
GET    /api/customers/search/plate/{plate} # Search by plate number
GET    /api/customers/                    # Get all customers (paginated)
GET    /api/customers/{id}                # Get customer detail
PUT    /api/customers/{id}                # Update customer
DELETE /api/customers/{id}                # Delete customer (admin only)
GET    /api/customers/{id}/transactions   # Get customer transaction history
```

### Transaction Endpoints
```
POST   /api/transactions/                 # Create new transaction
GET    /api/transactions/                 # Get all transactions (filtered by role)
GET    /api/transactions/{id}             # Get transaction detail
PUT    /api/transactions/{id}             # Update transaction
PATCH  /api/transactions/{id}/status      # Update transaction status
POST   /api/transactions/{id}/start-work  # Start work (employee)
POST   /api/transactions/{id}/calculate-cost # Calculate total cost (admin)
POST   /api/transactions/{id}/finalize    # Finalize transaction (admin)
POST   /api/transactions/{id}/mark-paid   # Mark as paid
GET    /api/transactions/{id}/history     # Get status history
```

### Report Endpoints
```
POST   /api/reports/                      # Create draft report
GET    /api/reports/                      # Get all reports (filtered by role)
GET    /api/reports/pending-approval      # Get reports needing approval (admin)
GET    /api/reports/{id}                  # Get report detail
PUT    /api/reports/{id}                  # Update draft/rejected report
POST   /api/reports/{id}/submit           # Submit for approval
POST   /api/reports/{id}/approve          # Approve report (admin)
POST   /api/reports/{id}/reject           # Reject report (admin)
DELETE /api/reports/{id}                  # Delete draft report
GET    /api/reports/transaction/{id}      # Get all reports for transaction
GET    /api/reports/export/excel          # Export to Excel (admin)
```

## 🛡️ Security & Permissions

### Admin Permissions
- ✅ Manage all customers, transactions, reports
- ✅ Approve/reject reports
- ✅ Calculate costs and finalize transactions
- ✅ Export data
- ✅ View all system data

### Employee Permissions
- ✅ View assigned transactions
- ✅ Create/edit own draft reports
- ✅ Submit reports for approval
- ✅ View own report history
- ❌ Cannot approve reports
- ❌ Cannot finalize transactions

## 📊 Database Schema Updates

### Customer Table
- Added indexed `plate_number` for fast lookup
- Vehicle information integrated

### Transaction Table
- Added `total_cost` field
- Enhanced status enum
- Foreign key to customer

### Report Table
- Added `rejection_reason` field
- Enhanced status workflow
- Approval tracking with timestamp

### History Table
- Added `created_by` for audit trail
- Tracks all status changes

## 🚀 Implementation Tips

### Frontend Integration
```javascript
// Scan plat nomor
const searchCustomer = async (plateNumber) => {
  const response = await fetch(`/api/customers/search/plate/${plateNumber}`);
  if (response.ok) {
    const customer = await response.json();
    // Auto-populate form with customer data
  }
};

// Create transaction
const createTransaction = async (customerId, complaint) => {
  const response = await fetch('/api/transactions/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ customer_id: customerId, complaint })
  });
};

// Employee create report with photo
const createReport = async (transactionId, description, photo) => {
  const formData = new FormData();
  formData.append('transaction_id', transactionId);
  formData.append('description', description);
  if (photo) formData.append('image', photo);
  
  const response = await fetch('/api/reports/', {
    method: 'POST',
    body: formData
  });
};
```

### Mobile App Workflow
1. **Login** → Get JWT token
2. **Scan QR/Barcode** → Search customer by plate
3. **Offline Mode** → Store drafts locally
4. **Sync** → Upload when online
5. **Push Notifications** → Approval status updates

## 📈 Monitoring & Analytics

### Key Metrics to Track
- Average repair time per transaction
- Employee productivity (reports per day)
- Approval rate vs rejection rate
- Customer satisfaction scores
- Revenue per transaction

### Reports Available
- Daily/Monthly revenue reports
- Employee performance reports
- Customer transaction history
- Pending approvals dashboard

## 🔧 Maintenance & Support

### Regular Tasks
- Database backup and maintenance
- Image storage cleanup
- Performance monitoring
- Security updates

### Troubleshooting
- Check transaction status flow
- Verify report approval chain
- Monitor API response times
- Review error logs