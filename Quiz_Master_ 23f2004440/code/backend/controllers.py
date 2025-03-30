from flask import render_template, request, redirect, url_for, session, flash
from flask import current_app as app
from backend.models import *
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# route for home page
@app.route('/')
def index():    
    return render_template('default.html')
#route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':#takes data from server
        return render_template('login.html')
    
    if request.method == 'POST':#sends data to the server
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
       
        user = User.query.filter_by(username=username).first()
        
        if user is None:    
            flash('User not found. Please register first.', 'error')
            return redirect(url_for('register'))#redirects to the register page
        
        if user.password_hash == password: 
            session['user_id'] = user.id
            session['username'] = user.username
            if user.is_admin:  
                    session['is_admin'] = True  
                    return redirect(url_for('admin_dashboard'))
            else:
                    session['is_admin'] = False
                    return redirect(url_for('dashboard', username=user.username))
            
        else:
            flash('Invalid password.Please try again', 'error')
            return render_template('login.html')
        
#route for register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('Please fill in all fields required', 'error')
            return render_template('register.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('This username already exists', 'error')
            return render_template('register.html')
        
        
        new_user = User(
            username=username,
            email=email,
            password_hash=password,  
            is_admin=False
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()#if an error occured just in case
            flash('An error occurred during registration', 'error')
            return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
#route for dashboard page if logged in as a user
@app.route('/dashboard/<username>')
def dashboard(username):
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    available_quizzes = Quiz.query.filter_by(is_active=True).filter(
    ~Quiz.scores.any(Score.user_id == user.id)
).all()
#first checks if the quiz is active or not then checks if the scores for that quiz is there for user or not, if there is no score avialable then it will show the available quizzes

    user_scores = Score.query.filter_by(user_id=user.id).all()
    
    return render_template('dashboard.html', 
                         user=user, 
                         scores=user_scores,
                         available_quizzes=available_quizzes)


#route for taking a quiz
@app.route('/quizzes/<int:quiz_id>')
def take_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz/take_quiz.html', quiz=quiz)
#route for submitting a quiz using post method which will send data to the server
@app.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    user_id = session['user_id']
    
  #calculation of scores
    total_scored = 0
    total_possible = 0
    for question in quiz.questions:
        total_possible += question.points
        answer = request.form.get(f'question_{question.id}')
        if answer and int(answer) == question.correct_option:
            total_scored += question.points
    
    # Save score to database
    score = Score(
        quiz_id=quiz.id,
        user_id=user_id,
        total_scored=total_scored,
        total_possible=total_possible
    )
    db.session.add(score)
    db.session.commit()
    
    return redirect(url_for('quiz_results', score_id=score.id))

# route for results of quiz attempted by the user
@app.route('/quiz_results/<int:score_id>')
def quiz_results(score_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    score = Score.query.get_or_404(score_id)
    if score.user_id != session['user_id']:
        return redirect(url_for('dashboard', username=User.query.get(session['user_id']).username))
    
    return render_template('quiz/results.html', score=score)
# route for dashboard if admin loggs in
@app.route('/admin/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('You have to be admin for this','warning')
        return redirect(url_for('login'))
    
# basic counts/statistics for admin dashboard
    subjects = Subject.query.all()
    chapters_count = Chapter.query.count()
    users_count = User.query.count()
    quizzes_count = Quiz.query.count()
    
    return render_template('admin/admin_dashboard.html',
                         subjects=subjects,
                         chapters_count=chapters_count,
                         users_count=users_count,
                         quizzes_count=quizzes_count)
# route for admin search
@app.route('/admin/search')
def admin_search():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    query = request.args.get('query', '').strip()
    search_type = request.args.get('type', 'all')
    
    if not query:
        flash('Please enter a search term', 'error')
        return redirect(url_for('admin_dashboard'))
    
    results = {
        'users': [],
        'subjects': [],
        'quizzes': []
    }
    
    if search_type in ['all', 'users']:
        results['users'] = User.query.filter(
            (User.username.ilike(f'%{query}%')) |
            (User.email.ilike(f'%{query}%'))
        ).all()
    
    if search_type in ['all', 'subjects']:
        results['subjects'] = Subject.query.filter(
            (Subject.name.ilike(f'%{query}%')) |
            (Subject.description.ilike(f'%{query}%'))
        ).all()
    
    if search_type in ['all', 'quizzes']:
        results['quizzes'] = Quiz.query.filter(
            (Quiz.title.ilike(f'%{query}%')) |
            (Quiz.remarks.ilike(f'%{query}%'))
        ).all()
    
    return render_template('admin/search_results.html',
                         query=query,
                         search_type=search_type,
                         results=results)
# route for user search
@app.route('/user/search')
def user_search():
   
    query = request.args.get('query', '').strip()
    search_type = request.args.get('type', 'all')
    
    results = {
        'subjects': [],
        'quizzes': []
    }
    
   
    if search_type in ['all', 'subjects']:
        results['subjects'] = Subject.query.filter(
            (Subject.name.ilike(f'%{query}%'))
        ).all()
    
    if search_type in ['all', 'quizzes']:
        results['quizzes'] = Quiz.query.filter(
            (Quiz.title.ilike(f'%{query}%')) 
        ).all()
    
    return render_template('user_search.html',
                         query=query,
                         search_type=search_type,
                         results=results)

#subjects route for admin
@app.route('/admin/subjects', methods=['GET'])
def list_subjects():#will display all the subjects
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)
#so that admin can create  new subjects
@app.route('/admin/subjects/new', methods=['GET', 'POST'])
def create_subject():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        subject = Subject(
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for('list_subjects'))
    return render_template('admin/subject_form.html')
#so that admin can edit subjects
@app.route('/admin/subject/<int:subject_id>/edit', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Subjectname is required', 'error')
            return render_template('admin/subject_form.html', subject=subject)
        
        subject.name = name
        subject.description = description
        db.session.commit()
        
        flash('Subject  has been updated', 'success')
        return redirect(url_for('view_subject', subject_id=subject.id))
    
    return render_template('admin/subject_form.html', subject=subject)
#route for deleting subjects 
@app.route('/admin/subject/<int:subject_id>/delete')
def delete_subject(subject_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    subject = Subject.query.get_or_404(subject_id)
    #if a subject is deleted all the content inside it will be deleted
    
    for chapter in subject.chapters:
        for quiz in chapter.quizzes:
            db.session.delete(quiz)
        db.session.delete(chapter)
    
    db.session.delete(subject)
    db.session.commit()
    
    flash('Subject and all its content  has been deleted', 'success')
    return redirect(url_for('admin_dashboard'))
#route for displaying any particular subject
@app.route('/admin/subject/<int:subject_id>')
def view_subject(subject_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    subject = Subject.query.get_or_404(subject_id)
    return render_template('admin/view_subject.html', subject=subject)

#route for displaying any particular user to admin
@app.route('/admin/user/<int:user_id>')
def view_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    return render_template('admin/users.html', user=user)
#route for creating new chapters by admin inside a particular subject
@app.route('/admin/subject/<int:subject_id>/chapter/new', methods=['GET', 'POST'])
def create_chapter(subject_id):
    if not session.get('is_admin'):
        flash('You have to be admin for this','warning')
        return redirect(url_for('login'))
    
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        chapter = Chapter(
            subject_id=subject.id,
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(chapter)
        db.session.commit()
        
        flash('Chapter created successfully!', 'success')
        return redirect(url_for('view_subject', subject_id=subject.id))
    
    return render_template('admin/chapter_form.html', subject=subject)
#route for editing chapters
@app.route('/admin/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    if not session.get('is_admin'):
        flash('You have to be admin for this','warning')
        return redirect(url_for('login'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.description = request.form.get('description')
        db.session.commit()
        
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('view_subject', subject_id=chapter.subject_id))
    
    return render_template('admin/chapter_form.html', chapter=chapter, subject=chapter.subject)
#route for viewing any particular chapter by admin
@app.route('/admin/chapter/<int:chapter_id>')
def view_chapter(chapter_id):
   
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('admin/view_chapter.html', chapter=chapter)
#route for deleting chapters
@app.route('/admin/chapter/<int:chapter_id>/delete')
def delete_chapter(chapter_id):
    if not session.get('is_admin'):
        flash('You have to be admin for this','warning')
        return redirect(url_for('login'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    
    db.session.delete(chapter)
    db.session.commit()
    
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('view_subject', subject_id=subject_id))
#route for creating new quizzes inside a particular chapter
@app.route('/admin/chapter/<int:chapter_id>/quiz/new', methods=['GET', 'POST'])
def create_quiz(chapter_id):
    if not session.get('is_admin'):
        flash('You have to be admin for this','warning')
        return redirect(url_for('login'))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        quiz = Quiz(
            chapter_id=chapter.id,
            title=request.form.get('title'),
            remarks=request.form.get('remarks'),
            duration_minutes=request.form.get('duration_minutes', type=int),
            passing_percentage=request.form.get('passing_percentage', type=int),
            is_active='is_active' in request.form
        )
        db.session.add(quiz)
        db.session.commit()
        
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('view_chapter', chapter_id=chapter.id))
    
    return render_template('admin/quiz_form.html', chapter=chapter)
#route for editing quizzes by admin
@app.route('/admin/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    if not session.get('is_admin'):
        flash('You have to be admin for this','warning')
        return redirect(url_for('login'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        quiz.title = request.form.get('title')
        quiz.remarks = request.form.get('remarks')
        quiz.duration_minutes = request.form.get('duration_minutes', type=int)
        quiz.passing_percentage = request.form.get('passing_percentage', type=int)
        quiz.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('view_quiz', quiz_id=quiz.id))
    
    return render_template('admin/quiz_form.html', quiz=quiz, chapter=quiz.chapter)
#route for viewing any particular quiz
@app.route('/admin/quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('admin/view_quiz.html', quiz=quiz)
#route for deleting quizzes
@app.route('/admin/quiz/<int:quiz_id>/delete')
def delete_quiz(quiz_id):
    if not session.get('is_admin'):
        flash('You have to be admin for this','warning')
        return redirect(url_for('login'))
        
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter_id = quiz.chapter_id
    
    db.session.delete(quiz)
    db.session.commit()
    
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('view_chapter', chapter_id=chapter_id))

#route for creating new questions inside a particular quiz
@app.route('/admin/quiz/<int:quiz_id>/question/new', methods=['GET', 'POST'])
def create_question(quiz_id):
    if not session.get('is_admin'):
        flash('You have to be admin for this','warning')
        return redirect(url_for('login'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        question = Question(
            quiz_id=quiz.id,
            question_statement=request.form.get('question_statement'),
            option1=request.form.get('option1'),
            option2=request.form.get('option2'),
            option3=request.form.get('option3'),
            option4=request.form.get('option4'),
            correct_option=request.form.get('correct_option', type=int),#only one correct option will be there
            points=request.form.get('points', type=float, default=1.0)#we can change the values 
        )
        db.session.add(question)
        db.session.commit()
        
        flash('Question  has been added successfully!', 'success')
        return redirect(url_for('view_quiz', quiz_id=quiz.id))
    
    return render_template('admin/question_form.html', quiz=quiz)
#route for viewing any particular question
@app.route('/admin/question/<int:question_id>')
def view_question(question_id):
    if not session.get('is_admin'):
        flash('You have to be admin for this','warning')
        return redirect(url_for('login'))
    
    question = Question.query.get_or_404(question_id)
    return render_template('admin/view_question.html', question=question)
#route for editing questions in quiz
@app.route('/admin/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    question = Question.query.get_or_404(question_id)
    # will take all the details of questions like question statement,option1,option2,option3,option4,correct_option,points
    if request.method == 'POST':
        question.question_statement = request.form.get('question_statement')
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')
        question.correct_option = request.form.get('correct_option', type=int)
        question.points = request.form.get('points', type=float, default=1.0)
        
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('view_quiz', quiz_id=question.quiz_id))
    
    return render_template('admin/question_form.html', question=question, quiz=question.quiz)
#route for deleting questions in quiz
@app.route('/admin/question/<int:question_id>/delete')
def delete_question(question_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('view_quiz', quiz_id=quiz_id))

#route for admin dashboard summary,will display the number of quizzes per subject and average quiz scores
@app.route('/admin-summary', methods=['GET'])
def admin_summary():
    subjects = Subject.query.all()
    quizzes = Quiz.query.all()
    scores = Score.query.all()
    
 
    subject_names = [sub.name for sub in subjects]
    quiz_counts = [len(sub.chapters) for sub in subjects]
    plt.figure()
    plt.bar(subject_names, quiz_counts, color='skyblue')
    plt.title('Number of Quizzes per Subject')
    plt.xlabel('Subjects')
    plt.ylabel('Quizzes Count')
    quiz_per_subject_plot = "static/images/quiz_per_subject.png"
    plt.savefig(quiz_per_subject_plot)
    plt.close()
    
    
    avg_scores = [sum([s.total_scored for s in q.scores]) / len(q.scores) if q.scores else 0 for q in quizzes]
    quiz_titles = [q.title for q in quizzes]
    plt.figure()
    plt.barh(quiz_titles, avg_scores)
    plt.title('Average Quiz Scores')
    plt.xlabel('Scores')
    plt.ylabel('Quizzes')
    avg_scores_plot = "static/images/avg_scores.png"
    plt.savefig(avg_scores_plot)
    plt.close()
    
    return render_template('admin/admin_summary.html', subjects=subjects, quizzes=quizzes, scores=scores,
                           quiz_per_subject_plot=quiz_per_subject_plot,
                           avg_scores_plot=avg_scores_plot)
#route for student dashboard summary will display the student performance trend and average quiz scores
@app.route('/student-summary/<int:user_id>', methods=['GET'])
def student_summary(user_id):
    user = User.query.get(user_id)
    scores = Score.query.filter_by(user_id=user_id).all()
    quizzes = Quiz.query.all()
    
    quiz_titles = [s.quiz.title for s in scores]
    total_scores = [s.total_scored for s in scores]
    possible_scores = [s.total_possible for s in scores]
    
    
    plt.figure()
    plt.bar(quiz_titles, total_scores)
    plt.title('Student Performance Trend')
    plt.xlabel('Quizzes')
    plt.ylabel('Scores')
    plt.xticks(rotation=45)
    performance_plot = "static/images/performance.png"
    plt.savefig(performance_plot)
    plt.close()

   
    avg_scores = [sum([s.total_scored for s in q.scores]) / len(q.scores) if q.scores else 0 for q in quizzes]
    quiz_titles = [q.title for q in quizzes]
    plt.figure()
    plt.barh(quiz_titles, avg_scores)
    plt.title('Average Quiz Scores')
    plt.xlabel('Scores')
    plt.ylabel('Quizzes')
    avg_scores_plot = "static/images/avg_scores.png"
    plt.savefig(avg_scores_plot)
    plt.close()
    
    return render_template('student_summary.html', user=user, scores=scores,
                           performance_plot=performance_plot)
