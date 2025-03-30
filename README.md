# Quiz App

## Overview
The *Quiz App* is a web-based application that allows users to take quizzes on various topics. It uses Flask, Jinja2, HTML, CSS, and Flask-SQLAlchemy for database management.

## Features
- User authentication (Login/Signup)
- Create, edit, and delete quizzes
- Multiple-choice questions
- Score tracking
- Responsive design

## Technologies Used
- *Backend*: Flask, Flask-SQLAlchemy
- *Frontend*: HTML, CSS, Jinja2
- *Database*: SQLite

## Installation

1. *Clone the Repository*
   sh
   git clone https://github.com/23f2004440/Quiz_master
   cd quiz-app
   

2. *Create a Virtual Environment*
   sh
   python -m venv venv
   source 'venv\Scripts\activate'
   

3. *Install Dependencies*
   sh
   pip install -r requirements.txt
   

4. *Set Up the Database*
   sh
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   

5. *Run the Application*
   sh
   flask run
   
   The app will be available at http://127.0.0.1:5000/

## Usage
- Register and log in.
- Create a new quiz(admin) or take an existing one.
- Answer multiple-choice questions and submit responses.
- View your score 


## Author
Developed by *Ayushi*.

