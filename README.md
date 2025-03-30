# Quiz Master 🎯
A Flask-based quiz platform that allows users to take quizzes and administrators to manage them.<br>
**
Features**
User & Admin Authentication<br>

Quiz Creation & Management<br>

Score Tracking & Performance Analysis<br>

Separate Dashboards for Users & Admins<br>

**Project Structure**<br>
bash<br>
Copy<br>
Edit<br>
/backend<br>
   ├── models.py        # Database Models<br>
   ├── controllers.py   # Routes & Logic<br>
/app.py                 # Main Flask App<br>
/requirements.txt       # Dependencies<br>
/templates              # HTML Templates<br>
/static                # CSS, JS, Images<br>
**Installation & Setup**
1️⃣ Clone the Repository<br>
bash<br>
Copy<br>
Edit<br>
git clone https://github.com/your-username/quiz-master.git<br>
cd quiz-master<br>
2️⃣ Set Up a Virtual Environment<br>
bash<br>
Copy<br>
Edit<br>
python -m venv venv<br>
source venv\Scripts\activate<br>
3️⃣ Install Dependencies<br>
bash<br>
Copy<br>
Edit<br>
pip install -r requirements.txt<br>
4️⃣ Initialize the Database
python<br>
Copy<br>
Edit<br>
python -c "from app import db; db.create_all()"<br>
5️⃣ Run the Flask App<br>
bash<br>
Copy<br>
Edit<br>
python app.py<br>
Access the app at http://127.0.0.1:5000 <br>

** Default Admin Login**
Username: admin
<br>
Password: admin123
<br>
** Tech Stack**
Backend: Flask, SQLAlchemy<br>

Frontend: HTML, Bootstrap<br>

Database: SQLite
<br>
