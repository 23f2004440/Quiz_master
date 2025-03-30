# Quiz Master 🎯
A Flask-based quiz platform that allows users to take quizzes and administrators to manage them.

📌 Features
User & Admin Authentication

Quiz Creation & Management

Score Tracking & Performance Analysis

Separate Dashboards for Users & Admins

📂 Project Structure
bash
Copy
Edit
/backend
   ├── models.py        # Database Models
   ├── controllers.py   # Routes & Logic
/app.py                 # Main Flask App
/requirements.txt       # Dependencies
/templates              # HTML Templates
/static                # CSS, JS, Images
🚀 Installation & Setup
1️⃣ Clone the Repository
bash
Copy
Edit
git clone https://github.com/your-username/quiz-master.git
cd quiz-master
2️⃣ Set Up a Virtual Environment
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
3️⃣ Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4️⃣ Initialize the Database
python
Copy
Edit
python -c "from app import db; db.create_all()"
5️⃣ Run the Flask App
bash
Copy
Edit
python app.py
Access the app at http://127.0.0.1:5000 🌍

👤 Default Admin Login
Username: admin

Password: admin123

🛠 Tech Stack
Backend: Flask, SQLAlchemy

Frontend: HTML, Bootstrap

Database: SQLite
