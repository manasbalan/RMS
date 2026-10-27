# RMS Pro - Intelligent Restaurant Management System

A full-stack, enterprise-grade restaurant management and operations suite built with **Python Flask** and an interactive, modern **glassmorphic dashboard**.

---

## 🚀 Quick Start

### Option 1: Double-Click Launcher (Windows)
Simply double-click `run.bat` in the project root. It will check dependencies, launch the server, and open `http://127.0.0.1:5000/` in your browser.

### Option 2: PowerShell
```powershell
.\start.ps1
```

### Option 3: Manual Startup
1. Install prerequisites:
   ```bash
   pip install -r requirements.txt
   ```
2. Start backend server:
   ```bash
   cd backend
   python app.py
   ```
3. Open `http://127.0.0.1:5000/` in your web browser.

---

## 🔑 Owner Access Credentials
Default pre-filled credentials for the portal:
* **Access ID:** `owner@restaurant.com`
* **Security Key:** `password`

---

## 🛠️ System Features & Modules

### 1. 📊 Executive Dashboard
* Real-time metrics: Active Customers, Reservations Today, Fulfilled Orders, Total Gross Revenue.
* Real-time operational dispatch notifications.

### 2. 👤 Customers & Floor Management
* **Customer Directory:** Register new customers and browse existing customer profiles with contact info and addresses.
* **Interactive Floor Map:** Visual grid of restaurant tables with 1-click status cycling (`Available` ➔ `Occupied` ➔ `Reserved`).

### 3. 🍕 Menu Management & Quick POS Billing Cart
* Categorized items (Food, Drinks, Desserts) with live search and price formatting.
* Dynamic **Add Item** modal and 1-click removal.
* Live Cart calculator with instant subtotal and tax calculation.

### 4. 📦 Live Order Pipeline (Kanban & Chef View)
* 3-stage visual pipeline: **New Incoming** ➔ **Preparing** ➔ **Delivered**.
* Lists item breakdown for each ticket (e.g. `2x Margherita Pizza`, `1x Espresso`).
* Supports both **Drag-and-Drop** and **1-click stage advancement buttons** (`🍳 Prepare`, `✅ Deliver`).

### 5. 🏷️ Stock Inventory & Automated Low-Stock Alerts
* Real-time tracking of ingredients, thresholds, and assigned suppliers.
* Automated low-stock indicator tag when stock drops below threshold.
* Instant restock dialog with custom quantity increment.

### 6. 🏭 Suppliers Directory
* Register and track ingredient and beverage suppliers with direct contact channels.

### 7. 🧾 Automated Billing & Tax Invoices
* Generates orders and official receipt invoices with 8% tax calculation.
* **Printable Receipt Modal:** High-resolution receipt generator supporting thermal and standard paper printing (`Ctrl+P` or **Print Receipt** button).

### 8. 👥 Staff & Personnel Roll
* Team member directory with roles (Lead Chef, GM, Server, Fleet Dispatch) and monthly payroll figures.

### 9. 📈 DBMS Analytics & Audit Export
* Comprehensive managerial reporting on gross revenue, invoice totals, inventory status, and supplier network.
* **📥 Export Comprehensive CSV:** 1-click consolidated export of all financial invoices, live orders, and stock records for accounting and audit.

### 10. 💬 Guest Feedback & Sentiment
* Customer review submission with star ratings (1 to 5) and feedback sentiment stream.

---

## 📁 Directory Structure
```
c:\manas others\restaurant\
│
├── backend\
│   ├── app.py              # Flask REST API + Database & Static Server
│   ├── restaurant.db       # SQLite database (auto-seeded)
│   ├── requirements.txt    # Python package dependencies
│   └── .env                # Port & database configuration
│
├── frontend\
│   └── index.html          # Single-Page Application (HTML5, Glassmorphism CSS, Vanilla JS)
│
├── requirements.txt        # Top-level dependencies
├── run.bat                 # 1-click Windows startup batch script
├── start.ps1               # PowerShell startup script
└── README.md               # Documentation & user guide
```
