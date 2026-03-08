# JeevanMeds

## Smart Medicine Platform with Expired Medicine Take‑Back System

JeevanMeds is a healthcare platform that combines **online pharmacy
services, medicine lifecycle management, and an expired medicine
take‑back system**.

The platform enables users to purchase medicines, track orders, and
safely return expired medicines. Pharmacies collect expired medicines
using QR verification, and administrators ensure proper biomedical
disposal.

This system promotes **safe medicine usage, environmental
sustainability, and responsible healthcare practices**.

------------------------------------------------------------------------

# Project Motivation

Expired medicines stored at home can cause:

-   Accidental consumption
-   Environmental contamination
-   Unsafe disposal practices

Most pharmacy platforms only focus on **medicine delivery**.\
They lack structured mechanisms for **tracking expired medicines and
disposing them safely**.

JeevanMeds solves this problem by implementing a **complete medicine
lifecycle management system**.

------------------------------------------------------------------------

# Key Features

## User Features

-   User registration and login
-   Medicine browsing and search
-   Add to cart and checkout
-   Order history
-   Expired medicine return request
-   QR code generation for pickup verification

------------------------------------------------------------------------

## Pharmacy Panel

Pharmacy users manage medicine inventory and expired medicine pickup
operations.

Features include:

-   Medicine management
-   Batch‑based inventory management
-   FEFO stock deduction (First Expiry First Out)
-   Order management
-   Expired medicine request verification
-   QR code scanning for collection

------------------------------------------------------------------------

## Admin Panel

Admin ensures safe disposal and monitors system activity.

Admin capabilities:

-   Dashboard analytics
-   Audit logging system
-   Disposal management
-   Disposal method tracking

------------------------------------------------------------------------

# System Roles

### Customer

-   Browse medicines
-   Place orders
-   Request expired medicine pickup
-   Show QR code during pickup

### Pharmacy

-   Manage medicines
-   Manage inventory batches
-   Verify expired requests
-   Scan QR codes
-   Collect expired medicines

### Admin

-   Monitor system statistics
-   View audit logs
-   Confirm final medicine disposal

------------------------------------------------------------------------

# System Architecture

``` mermaid
graph TD

User[Customer]
Pharmacy[Pharmacy Panel]
Admin[Admin Panel]

User -->|Order Medicines| Platform[JeevanMeds Platform]
User -->|Expired Medicine Request| Platform

Platform --> Pharmacy
Pharmacy -->|Inventory Management| Database[(MongoDB)]
Pharmacy -->|QR Collection| Platform

Admin -->|Audit Logs| Platform
Admin -->|Final Disposal| Platform

Platform --> Database
```

------------------------------------------------------------------------

# High Level Architecture (HLD)

``` mermaid
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

------------------------------------------------------------------------

# Medicine Lifecycle Diagram

``` mermaid
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

------------------------------------------------------------------------

# Expired Medicine Collection Flow

``` mermaid
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

------------------------------------------------------------------------

# Disposal Workflow

``` mermaid
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

------------------------------------------------------------------------

# Database Entity Relationship Diagram (ERD)

``` mermaid
erDiagram

USER ||--o{ ORDER : places
USER ||--o{ EXPIRED_REQUEST : submits

MEDICINE ||--o{ INVENTORY_BATCH : has
MEDICINE ||--o{ ORDER_ITEM : contains

ORDER ||--|{ ORDER_ITEM : includes

EXPIRED_REQUEST }o--|| USER : created_by

AUDIT_LOG }o--|| USER : performed_by
```

------------------------------------------------------------------------

# Project Structure

    app
    │
    ├── config
    │   ├── settings.py
    │   ├── constants.py
    │   └── roles.py
    │
    ├── extensions
    │   ├── database.py
    │   ├── login_manager.py
    │   └── storage.py
    │
    ├── models
    │   ├── user.py
    │   ├── medicine.py
    │   ├── inventory_batch.py
    │   ├── order.py
    │   ├── expired_request.py
    │   └── audit_log.py
    │
    ├── routes
    │   ├── auth_routes.py
    │   ├── main_routes.py
    │   ├── pharmacy_routes.py
    │   └── admin_routes.py
    │
    ├── templates
    │   ├── main
    │   ├── pharmacy
    │   └── admin
    │
    └── utils
        └── audit_logger.py

------------------------------------------------------------------------

# Technology Stack

### Backend

-   Python
-   Flask
-   MongoDB
-   MongoEngine ODM

### Frontend

-   HTML
-   CSS
-   Bootstrap
-   JavaScript

### Tools & Libraries

-   Chart.js (Admin analytics)
-   jsQR (QR scanning)
-   QR Code API

------------------------------------------------------------------------

# Audit Logging System

Important actions are recorded for transparency.

Example logs:

    12 Mar 2026 14:20  Pharmacy_01  ADD_BATCH
    Added batch B023 (Paracetamol)

    12 Mar 2026 15:05  User_22  ORDER_PLACED
    Order ₹350

    12 Mar 2026 18:00  Admin  DISPOSE_MEDICINE
    Crocin disposed via Incineration

------------------------------------------------------------------------

# Environmental Impact

JeevanMeds promotes responsible medicine disposal by:

-   Preventing unsafe household storage
-   Reducing pharmaceutical contamination
-   Ensuring proper biomedical waste disposal

------------------------------------------------------------------------

# Future Enhancements

Possible improvements include:

-   AI based medicine expiry detection
-   Barcode scanning for medicines
-   Mobile application support
-   Automated expiry alerts
-   Healthcare regulatory integration

------------------------------------------------------------------------

# Conclusion

JeevanMeds provides a **complete digital ecosystem for managing the
medicine lifecycle** from purchase to safe disposal.

By combining e‑commerce functionality, QR verification, and disposal
management, the platform enhances healthcare safety and promotes
environmental sustainability.
