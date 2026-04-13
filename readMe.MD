<h1>
  <img src="app/static/project.ico" width="30" height="30" style="vertical-align: middle;">
  DawaiTrack
</h1>
<img src="img/overview.png" style="vertical-align: middle;">

### Smart Medicine Platform with Expired Medicine Take-Back System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web_Framework-black.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Project-Active-brightgreen.svg)
![Vercel](https://vercelbadge.vercel.app/api/anshulwycliffe/dawaitrack)
---

## 📌 Overview

DawaiTrack is a healthcare platform that combines **online pharmacy services, medicine lifecycle management, and an expired medicine take-back system**.

The platform enables users to purchase medicines, track orders, and safely return expired medicines. Pharmacies collect expired medicines using QR verification, and administrators ensure proper biomedical disposal.

This system promotes **safe medicine usage, environmental sustainability, and responsible healthcare practices**.
Demo Video : [Link](https://youtu.be/vsHEX82ymVE?si=PvVjAsqjYL_1UsNu)
---

## 🎯 Project Motivation

Expired medicines stored at home can cause:

* Accidental consumption
* Environmental contamination
* Unsafe disposal practices

Most pharmacy platforms only focus on **medicine delivery**.
They lack structured mechanisms for **tracking expired medicines and disposing them safely**.

---

## 🚀 Key Features

### 👤 User Features

* User registration and login
* Medicine browsing and search
* Add to cart and checkout
* Order history
* Expired medicine return request
* QR code generation for pickup verification

---

### 🏥 Pharmacy Panel

* Medicine management
* Batch-based inventory management
* FEFO stock deduction (First Expiry First Out)
* Order management
* Expired medicine request verification
* QR code scanning for collection

---

### 🛠 Admin Panel

* Dashboard analytics
* Audit logging system
* Disposal management
* Disposal method tracking

---

## 👥 System Roles

### Customer

* Browse medicines
* Place orders
* Request expired medicine pickup
* Show QR code during pickup

### Pharmacy

* Manage medicines
* Manage inventory batches
* Verify expired requests
* Scan QR codes
* Collect expired medicines

### Admin

* Monitor system statistics
* View audit logs
* Confirm final medicine disposal

---

## ⚙️ System Architecture

```mermaid
graph TD
User[Customer]
Pharmacy[Pharmacy Panel]
Admin[Admin Panel]

User -->|Order Medicines| Platform[DawaiTrack Platform]
User -->|Expired Medicine Request| Platform

Platform --> Pharmacy
Pharmacy -->|Inventory Management| Database[(MongoDB)]
Pharmacy -->|QR Collection| Platform

Admin -->|Audit Logs| Platform
Admin -->|Final Disposal| Platform

Platform --> Database
```

---

## 🧠 High Level Architecture (HLD)

```mermaid
flowchart LR
Client[Web Browser / Frontend]
Server[Flask Backend]
DB[(MongoDB Database)]

Client --> Server
Server --> DB

Server --> UserModule
Server --> PharmacyModule
Server --> AdminModule

UserModule --> DB
PharmacyModule --> DB
AdminModule --> DB
```

---

## 🔄 Medicine Lifecycle

```mermaid
flowchart TD
A[Medicine Manufactured]
B[Inventory Batch Added]
C[Medicine Purchased by User]
D[Medicine Expired]
E[User Requests Expired Pickup]
F[Pharmacy Approves Request]
G[Pharmacy Collects via QR]
H[Admin Confirms Disposal]

A --> B
B --> C
C --> D
D --> E
E --> F
F --> G
G --> H
```

---

## 🔁 Expired Medicine Collection Flow

```mermaid
sequenceDiagram
participant User
participant Pharmacy
participant System
participant Admin

User->>System: Submit Expired Medicine Request
System->>Pharmacy: Notify Request

Pharmacy->>System: Approve Request

User->>Pharmacy: Show QR Code
Pharmacy->>System: Scan QR

System->>Pharmacy: Mark as COLLECTED

Pharmacy->>Admin: Send for Disposal
Admin->>System: Confirm DISPOSED
```

---

## ♻️ Disposal Workflow

```mermaid
flowchart LR
Collected[Collected Medicines]
AdminCheck[Admin Verification]

Method1[Incineration]
Method2[Autoclaving]
Method3[Chemical Treatment]
Method4[Secure Landfill]

Collected --> AdminCheck

AdminCheck --> Method1
AdminCheck --> Method2
AdminCheck --> Method3
AdminCheck --> Method4
```

---

## 🧬 Database ER Diagram

```mermaid
erDiagram
USER ||--o{ ORDER : places
USER ||--o{ EXPIRED_REQUEST : submits

MEDICINE ||--o{ INVENTORY_BATCH : has
MEDICINE ||--o{ ORDER_ITEM : contains

ORDER ||--|{ ORDER_ITEM : includes

EXPIRED_REQUEST }o--|| USER : created_by
AUDIT_LOG }o--|| USER : performed_by
```

---

## 📁 Project Structure

```
DawaiTrack/
├── app/
│   ├── config/
│   ├── extensions/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   ├── static/
│   └── utils/
├── tests/
├── run.py
├── requirements.txt
└── README.md
```

---

## 🛠 Technology Stack

### Backend

* Python
* Flask
* MongoDB
* MongoEngine

### Frontend

* HTML
* CSS
* Bootstrap
* JavaScript

### Tools

* Chart.js
* jsQR
* QR Code API

---

## 🔐 API Endpoints

### Search
```
[GET] /api/search-suggestions?q=<query>
```
### Cart
```
[POST] /cart/add/<slug>
[GET] /cart
```
### Orders
```
[POST] /order/checkout
[GET] /order/history
```
### Expired Medicines
```
[POST] /expired/request
[GET] /expired/history
```
### Pharmacy
```
[POST] /pharmacy/expired-request/approve/<id>
[POST] /pharmacy/expired-request/collect/<id>
```
### Admin
```
[GET] /admin/dashboard
[GET] /admin/audit-logs
[POST] /admin/dispose
```
---

## 📸 Screenshots

> <img src="img/home.png"> Home Page

> <img src="img/medicine.png"> Medicine Search Page

> <img src="img/product.png"> Product Detail Page

> <img src="img/expired.png"> Expired Medicine Page (User)

> <img src="img/pharmacy.png"> Expired Medicine Request (Pharmacy Console)

> <img src="img/admin.png"> Audit Log (Admin Panel)


---

## ⚙️ Setup & Installation

### 1. Clone Repository

```
git clone https://github.com/anshulwycliffe/DawaiTrack.git
cd DawaiTrack
```

### 2. Install Dependencies

```
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env`:

```
SECRET_KEY=your_secret_key
MONGO_URI=mongodb://localhost:27017/dawaitrack
```

### 4. Run Application

```
python main.py
```

---

## Audit Logging System

Tracks:

* Orders
* Inventory
* Disposal

Important actions are recorded for transparency.

Example logs:

    [12 Mar 2026 14:20]  Pharmacy_01  ADD_BATCH
    Added batch B023 (Paracetamol)

    [12 Mar 2026 15:05]  User_22  ORDER_PLACED
    Order ₹350

    [12 Mar 2026 18:00]  Admin  DISPOSE_MEDICINE
    Crocin disposed via Incineration
---

## Environmental Impact

* Prevents unsafe storage
* Reduces pollution
* Ensures safe disposal

---

## Future Enhancements

* Mobile App
* AI alerts
* Barcode scanning
* Cloud scaling

---

## 📜 License

MIT License
Copyright © 2026 Anshul Wycliffe

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
---

## ✅ Conclusion

DawaiTrack provides a **complete medicine lifecycle ecosystem**, ensuring safe usage, verified collection, and responsible disposal.
