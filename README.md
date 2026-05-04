# PNG Compliance Hub 2026
### **High-End Tax Compliance SaaS for PNG MSMEs**

PNG Compliance Hub 2026 is a premium, mobile-first SaaS platform designed to empower Papua New Guinea's Micro, Small, and Medium Enterprises (MSMEs) to navigate the complex IRC tax landscape with ease. Built for the 2026 tax year, it combines legal precision with a modern "Oceania Dark" aesthetic and robust offline capabilities.

---

## 🚀 Core Features

### 1. 2026 IRC Tax Engine
Automated, legally-accurate calculations based on the 2026 PNG Tax Code:
*   **SWT (Salary & Wages Tax)**: Support for Resident and Non-Resident progressive brackets (22% – 42% bands).
*   **GST (Goods & Services Tax)**: Automated 10% calculation with integrated **Input Tax Credit (ITC)** logic for expense recovery.
*   **SBT (Small Business Tax)**: Intelligent eligibility detection and turnover-based calculation (K400 flat fee or 2% of turnover).

### 2. PWA & Offline-First Design
Engineered for PNG's unique connectivity environment:
*   **Service Worker Integration**: Core app assets are cached for offline accessibility.
*   **Offline Data Logging**: Log sales and expenses even without a network. Data is stored in **IndexedDB** and automatically synced when back online.
*   **Connectivity Indicator**: Real-time "Pulse" indicator (Online/Offline) in the dashboard.

### 3. Biometric Authentication (WebAuthn)
*   **Passwordless Login**: Secure your business data using Fingerprint, FaceID, or hardware keys (Windows Hello / Apple TouchID).
*   **Device Management**: Register and manage multiple biometric devices from your profile.

### 4. High-Fidelity IRC Reporting
*   **Digital Form Replicas**: Generate official-looking **GSTS65A**, **SWT Remittance**, and **SBT Declaration** forms.
*   **Professional Iconography**: Standardized **Bootstrap Icons** (v1.11.3) throughout the platform for an enterprise-grade aesthetic.
*   **Print-to-PDF**: Optimized CSS layouts allow for one-click PDF generation or professional physical printing.

---

## 🛠️ Technical Stack

*   **Backend**: Python 3.12+ & Django 6.0 (High-performance, secure MVC framework).
*   **Frontend**: 
    *   **Bootstrap 5.3**: Responsive mobile-first foundation.
    *   **HTMX**: Lightning-fast, partial-page updates without full reloads.
    *   **Vanilla CSS**: Custom "Oceania Dark" glassmorphism theme.
*   **Database**: PostgreSQL (Production) / SQLite (Development).
*   **Authentication**: WebAuthn / FIDO2 (via `webauthn` library).
*   **Browser Storage**: IndexedDB (for offline queuing).

---

## 🧠 How the System Works

### 1. Business Onboarding
Upon registration, users are guided through a **Business Profile Setup**. The system collects the business's TIN, industry, province, and estimated turnover. This data is used to automatically configure the tax engines (e.g., determining if the business should file GST or SBT).

### 2. The Ledger System
The core of the app is the **Daily Ledger**. Users record Sales and Purchases.
*   The **GST Engine** monitors these entries to calculate Output GST (from sales) and Input GST (from purchases).
*   The **SBT Engine** monitors total annual turnover to ensure the business stays within compliance thresholds.

### 3. Compliance Dashboard
The dashboard provides a real-time **Compliance Score (0-100)** based on profile completeness and filing status. It visualizes revenue vs. tax liability using **Chart.js**, helping business owners plan for upcoming IRC payments.

### 4. Filing & Export
At the end of a tax period (Monthly/Quarterly/Annual), the system aggregates ledger data into a **Tax Return**.
*   The system generates a high-fidelity replica of the required IRC form.
*   Users can review the data, "Sign" the digital declaration, and export the form for submission to the IRC.

### 5. Offline Submission Flow
1.  **Detection**: The app detects a network failure and switches the UI to "Offline" mode.
2.  **Storage**: Form submissions (like a Quick Sale) are intercepted and saved to **IndexedDB**.
3.  **Sync**: When the browser detects connectivity, it triggers a **Background Sync** event. The Service Worker then sends the queued entries to the Django backend.

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**:
    ```bash
    git clone <repo-url>
    cd "PNG COMPLIANCE HUB 2026"
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**:
    Create a `.env` file based on `.env.example`:
    ```ini
    DEBUG=True
    SECRET_KEY=your-secret-key
    DATABASE_URL=sqlite:///db.sqlite3
    ```

4.  **Database Migration**:
    ```bash
    python manage.py migrate
    ```

5.  **Run Development Server**:
    ```bash
    python manage.py runserver
    ```

---

## 📅 Road Map 2026
*   [ ] **API Integration**: Direct digital filing to IRC e-Tax portal (when available).
*   [ ] **SMS Notifications**: Automated SMS reminders for tax due dates.
*   [ ] **Multi-Currency Support**: For MSMEs engaging in regional export.

---
**Developed for the MSMEs of Papua New Guinea.**
