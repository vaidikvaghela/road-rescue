# 🗺️ RoadRescue — High-Fidelity Vehicle Breakdown & Assistance Ecosystem

RoadRescue is a state-of-the-art, location-aware digital assistance ecosystem that connects stranded drivers with nearby repair shops, towing services, and professional mechanics in real-time. Whether dealing with a sudden highway blowout or scheduling custom vehicle upkeep, RoadRescue provides a high-fidelity, premium interface to ensure quick resolution, transparent pricing, and robust dispatch tracking.

---

## ✨ Primary Features

### 1. 🗺️ GPS-Aware Interactive Map & Service Discovery
- **Live Location Tracking**: Auto-geolocates the user with accuracy rings utilizing standard browser geolocation APIs.
- **Dynamic Nearness Filters**: Allows filtering of nearby service providers (Mechanics, Towing, Tire Repair, Battery Services) within configurable search radii.
- **Sleek Map Markers**: Features high-fidelity customized Leaflet.js markers displaying detailed provider cards, contact details, rating scores, and instant booking shortcuts.

### 2. 🚨 Live Emergency SOS & Status Tracking
- **One-Click Dispatch**: Standardized rapid SOS submission for swift mechanic allocation.
- **Stage-by-Stage Tracking**: Real-time visual timeline mapping the request’s progress (`Pending` ➡️ `Assigned` ➡️ `En Route` ➡️ `In Progress` ➡️ `Completed`).
- **Interactive Dispatches**: Integrates detailed provider comments and technician assignment names/contact details directly inside the tracking cards.

### 3. 📅 Non-Emergency Custom Service Requests
- **Tailored Bookings**: Customers can request custom, non-emergency service jobs directly from their chosen service provider profile.
- **Detailed Workorders**: Captures specific vehicle attributes (Make, Model, Year, Registration Number) along with customized problem descriptions.
- **Provider Dashboard Control**: Seamless accepting, declining, and progress tracking workspace designed specifically for mechanics and service shops.

### 4. 💳 Integrated Payments & UPI-Ready QR Codes
- **Billing System**: Seamless invoicing generated immediately upon request completion.
- **UPI QR Code Generator**: Renders dynamic, UPI-compliant QR codes displaying the exact payment amounts, scanable by standard mobile payment apps (Paytm, GPay, PhonePe, Bhim, etc.).
- **Interactive Payments**: Real-time simulation of secure transaction verification updating the request's status instantly upon completion.

### 5. ⭐ Premium Star-Rating & Testimonial Engine
- **Multi-Star Submissions**: Smooth, intuitive rating and comment interface integrated directly into paid request options.
- **Dynamic Testimonials**: A responsive review carousel featured on the landing page that dynamically loads and displays recent approved customer reviews.
- **Real-Time Analytics**: Dashboard statistics cards automatically update their counters (e.g., "Reviews Given") dynamically upon review submission.

### 6. 📊 Responsive Professional Dashboards
- **Tailored Workspace UI**: Adapts automatically based on the authenticated user's role (Driver vs. Service Provider).
- **Available Jobs Console**: Active provider console designed to alert technicians about unassigned emergencies and allow one-click job claiming.
- **Full Profile Editing**: Interactive glassmorphic forms for updating personal information, profile pictures, and active contact numbers.

---

## 🛠️ Technology Stack

- **Frontend**: High-fidelity modern HTML5, Vanilla JavaScript (ES6+), Leaflet.js Interactive Mapping, CSS3 Custom Properties (featuring neon glassmorphism and liquid backgrounds).
- **Backend Framework**: Python 3.11+, Django 4.2+, Django REST Framework (DRF) for rich RESTful APIs.
- **Security & Session**: JWT (JSON Web Tokens) with simple-jwt, secure CSRF-token handshake validations.
- **Database Engine**: SQLite 3 for localized lightweight data persistence.
- **Interface Aesthetics**: Google Fonts (Inter, Outfit), high-quality FontAwesome / Fluent Emojis, and customizable CSS Liquid Glass Filters.

---

## 🚀 Getting Started

### 📋 Prerequisites
Ensure you have the following installed on your machine:
- **Python 3.11** or higher
- **pip** package installer

### 🛠️ Step-by-Step Installation

**1. Clone the project and navigate to the directory:**
```bash
cd road-rescue-main
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Initialize Database Migrations:**
```bash
python manage.py makemigrations accounts services emergency core
python manage.py migrate
```

**4. Seed the Database with Sample Data:**
Populate your database with rich, mock service types, active nearby service providers, realistic custom service requests, and sample user profiles:
```bash
python manage.py seed_data
```

**5. Start the Development Server:**
```bash
python manage.py runserver
```
Visit the application in your browser at `http://127.0.0.1:8000/`.

---

## 🧭 Directory Navigation & Core Pages

| URL Route | Destination | Description |
|---|---|---|
| `/` | **Landing Page** | Map hub, emergency portal, dynamic user reviews list, and service type catalogs. |
| `/login/` | **Auth Login** | Premium login page accepting credentials for both customers and providers. |
| `/register/` | **User Registration** | Responsive user onboarding portal. |
| `/dashboard/` | **Customer/Provider Dashboard** | Real-time tracking boards, active jobs tables, profile editing, and review options. |
| `/admin/` | **Django Admin Console** | Backend supervision console utilizing a modernized Jazzmin design template. |
| `/api/docs/` | **Swagger API Docs** | High-fidelity interactive REST API documentation. |

---

## 📊 Pre-Configured Test Credentials

To assist you with testing the platform immediately, the database seeder creates standard administrative credentials:

### 🛡️ Administrator Access
- **Email**: `admin@roadrescue.com`
- **Password**: `admin123`

### 👤 Driver / Customer Account
- **Email**: `testuser12@gmail.com`
- **Password**: `testpassword123`

### 🔧 Service Provider Account
- **Email**: `testprovider12@gmail.com`
- **Password**: `testpassword123`

---

*Made with by Vaidik Vaghela 
