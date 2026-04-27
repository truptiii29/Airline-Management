**✈️ Airline Management System (AMS)**

A full-stack database-driven application designed to manage airline operations efficiently using modern web technologies and relational database principles.

**📌 Project Overview**

The Airline Management System (AMS) is developed to provide a centralized platform for managing core airline operations such as:

Flight scheduling
Passenger management
Ticket booking
Payment processing
Pilot and aircraft management

This system eliminates issues found in traditional systems like data redundancy, inconsistency, and inefficient data retrieval by using a structured and normalized relational database.

**🚀 Features**

🔹 Core Functionalities

Manage Airports, Aircrafts, Pilots, Flights
Passenger registration and management
Flight booking and seat allocation
Payment tracking and validation
Flight status monitoring

🔹 Database Features

Fully normalized database (up to 5NF)
Use of Primary Keys & Foreign Keys
Complex SQL queries:
Joins, Subqueries, Views
Aggregate Functions
Set Operations
Advanced DB concepts:
Triggers
Stored Procedures
Cursors
Transactions (ACID properties)

🔹 System Features

Secure and structured backend
User-friendly frontend interface
Real-time database interaction
Concurrency control using locking mechanisms

**🛠️ Tech Stack**

💻 Frontend
React.js
HTML5, CSS3
JavaScript

**⚙️ Backend**

Flask (Python)
REST APIs

**🗄️ Database**

MySQL
🔧 Tools & Libraries
SQLAlchemy (ORM)
Axios (API calls)
XAMPP / WAMP (Server)
Git & GitHub

**📂 Project Structure**

Airline-Management-System/
│
├── frontend/              # React frontend
├── backend/               # Flask backend
│   ├── config.py          # DB configuration
│   ├── run.py             # App entry point
│
├── database/              # SQL scripts (DDL, DML)
├── docs/                  # Project report & diagrams
├── screenshots/           # UI screenshots
└── README.md

**⚙️ Installation & Setup**

1️⃣ Clone the Repository
git clone https://github.com/your-username/airline-management-system.git
cd airline-management-system

2️⃣ Setup Backend (Flask)

cd backend
pip install -r requirements.txt

Update database config in config.py:

SQLALCHEMY_DATABASE_URI = "mysql://username:password@localhost/airline_management"

Run backend:

python run.py

3️⃣ Setup Database (MySQL)

Start MySQL server
Run SQL scripts:
CREATE DATABASE airline_management;
USE airline_management;
Import tables and data (DDL + DML scripts from project)

4️⃣ Setup Frontend (React)

cd frontend
npm install
npm start

▶️ How to Use

**👤 User Flow**

Open the application in browser
Register / Login
Search for available flights
Book tickets and select seats
Make payment
View booking history
👨‍💼 Admin Capabilities
Add/manage flights
Assign pilots and aircraft
Monitor bookings and revenue
Update flight status
🔒 Database Concepts Implemented

This project demonstrates strong DBMS fundamentals:

✔ Entity-Relationship Modeling
✔ Normalization (1NF → 5NF)
✔ Referential Integrity
✔ Transactions (COMMIT, ROLLBACK, SAVEPOINT)
✔ Concurrency Control (Locks)
✔ Triggers & Stored Procedures


**📖 Learning Outcomes**

Practical implementation of DBMS concepts
Real-world experience in full-stack development
Understanding of data integrity and optimization
Hands-on experience with SQL and backend integration

**🔮 Future Enhancements**

Online payment gateway integration
Real-time flight tracking
AI-based pricing system
Mobile application support
Role-based authentication system

**👨‍💻 Contributors**

Vaibhav Shrivastava

Trupti Ajit Jain
