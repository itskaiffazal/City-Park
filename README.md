# 🚗 City Park – Vehicle Parking App

A **Flask-based Vehicle Parking Management System** built as part of the **MAD-I project**.
The app supports **multi-user functionality (Admin + Users)**, allowing admins to manage parking lots and users to seamlessly book/release slots.

---

## 🌟 Features

### 👤 User Features:

* User Registration & Login
* Dashboard with active reservations
* Reserve the first available parking spot in a chosen lot
* Release a parking spot after use
* View parking history with timestamps & cost calculation

### 🛠️ Admin Features:

* Predefined Admin login (no registration required)
* Create, update, and delete parking lots
* Automatic creation of parking spots based on lot capacity
* View all registered users & their reservations
* View parking status (occupied/available spots)
* View summary reports & charts

### 🎨 UI/UX Features:

* Responsive design using **Bootstrap 5**
* Flash messages for user feedback
* Jinja2 templating with reusable layouts
* Simple and clean interface

---

## 🏗️ Tech Stack

* **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
* **Backend**: Python (Flask)
* **Database**: SQLite (programmatically created)
* **Templating**: Jinja2
* **Deployment**: Gunicorn + Render

---

## 📂 Project Structure

```
City-Park/
 ├── app.py               # Main Flask app
 ├── database.py          # Database initialization
 ├── models.py            # Models for User, Admin, Lot, Spot, Reservation
 ├── static/              # CSS, images
 ├── templates/           # Jinja2 templates
 ├── requirements.txt     # Dependencies
 ├── Procfile             # For deployment
 └── README.md            # Documentation
```

---

## ⚙️ Installation

1. **Clone the repository**

```bash
git clone https://github.com/itskaiffazal/City-Park.git
cd City-Park/City_Park_24F1002359
```

2. **Create virtual environment & activate**

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the app**

```bash
python app.py
```

5. Open in browser:
   👉 `http://127.0.0.1:5000`

---



---

## 🎥 Demo & 📑 Report

* 🌍 **Live Deployment** → [Click here](https://city-park.onrender.com)

---

## 🚀 Future Enhancements

* Payment gateway for automated billing
* Real-time IoT-based slot availability
* QR-code based entry/exit system
* Push notifications for slot reminders

---

## 👨‍💻 Author

Developed  by **Kaif Fazal**
📧 Contact: [24f1000149@ds.study.iitm.ac.in](mailto:24f1000149@ds.study.iitm.ac.in)
🔗 GitHub: [itskaiffazal](https://github.com/itskaiffazal)

---
