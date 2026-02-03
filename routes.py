from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from models import db, User, MentalHealthQuizResult, Message
from forms import LoginForm, SignupForm, RequestResetForm, ResetPasswordForm
from ai_analysis import analyze_mental_health
from google_utils import schedule_appointment_event
from sqlalchemy import or_, func
from flask_mail import Message as EmailMessage
from utils import mail
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def send_reset_email(user):
    token = user.get_reset_token()
    msg = EmailMessage('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('If an account exists with that email, a reset email has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', title='Reset Password', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Reset Password', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard.index'))
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.signup'))

        role = form.role.data

        if role == 'parent' and not form.child_registration_number.data:
            flash('Child Registration Number is required for Parents.', 'error')
        elif role == 'professional' and not form.professional_id.data:
            flash('Professional ID is required for Mental Health Professionals.', 'error')
        elif role == 'student' and not form.student_id.data:
            flash('Student ID is required for Students.', 'error')
        elif role == 'teacher' and not form.teacher_id.data:
            flash('Teacher ID is required for Teachers.', 'error')
        elif role == 'counselor' and not form.counselor_license.data:
            flash('Counselor License is required for School Counselors.', 'error')
        else:
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                role=role,
                approved=False if role == 'professional' else True,
                student_id=form.student_id.data if role == 'student' else None,
                teacher_id=form.teacher_id.data if role == 'teacher' else None,
                professional_id=form.professional_id.data if role == 'professional' else None,
                counselor_license=form.counselor_license.data if role == 'counselor' else None,
                child_registration_number=form.child_registration_number.data if role == 'parent' else None
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/signup.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    if current_user.role == 'student' or current_user.role == 'user':
        # Fetch own results
        results = MentalHealthQuizResult.query.filter_by(user_id=current_user.id).order_by(MentalHealthQuizResult.created_at.desc()).all()
        return render_template('dashboard/student_dashboard.html', results=results)
        
    elif current_user.role == 'parent':
        # Fetch child's results based on registration number match
        child_id = current_user.child_registration_number
        if child_id:
            child = User.query.filter_by(student_id=child_id).first()
            if child:
                results = MentalHealthQuizResult.query.filter_by(user_id=child.id).order_by(MentalHealthQuizResult.created_at.desc()).all()
                return render_template('dashboard/parent_dashboard.html', results=results, child=child)
            else:
                flash('Child account not found with the provided Registration Number.', 'warning')
        else:
             flash('No Child Registration Number linked.', 'warning')
        return render_template('dashboard/parent_dashboard.html', results=[], child=None)

    elif current_user.role == 'counselor':
        # Fetch high risk cases
        high_risk_results = MentalHealthQuizResult.query.filter_by(risk_level='High Risk')\
            .join(User).order_by(MentalHealthQuizResult.created_at.desc()).all()
        return render_template('dashboard/counselor_dashboard.html', results=high_risk_results)

    elif current_user.role == 'teacher':
        return render_template('dashboard/teacher_dashboard.html')
    elif current_user.role == 'professional':
        return render_template('dashboard/professional_dashboard.html')
    return redirect(url_for('auth.login'))

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    """
    Mental health survey route.
    """
    if request.method == 'POST':
        answers = request.form
        result = analyze_mental_health(answers)
        
        # Save result to DB
        new_result = MentalHealthQuizResult(
            user_id=current_user.id,
            score=result['score'],
            risk_level=result['status'],
            recommendation=result['recommendation']
        )
        db.session.add(new_result)
        db.session.commit()

        if result['status'] == 'High Risk':
             flash('Your results indicate High Risk. A notification has been sent to your counselor.', 'warning')
             # In a real app, we would send email/notification here
        
        return render_template('reports/result.html', result=result)
    return render_template('reports/quiz.html')

@reports_bp.route('/monthly_summary')
@login_required
def monthly_summary():
    if current_user.role not in ['counselor', 'professional', 'teacher']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Simple analytics for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    total_assessments = MentalHealthQuizResult.query.filter(MentalHealthQuizResult.created_at >= thirty_days_ago).count()
    high_risk_count = MentalHealthQuizResult.query.filter(MentalHealthQuizResult.created_at >= thirty_days_ago, MentalHealthQuizResult.risk_level == 'High Risk').count()
    avg_score = db.session.query(func.avg(MentalHealthQuizResult.score)).filter(MentalHealthQuizResult.created_at >= thirty_days_ago).scalar()
    
    stat_summary = {
        'total': total_assessments,
        'high_risk': high_risk_count,
        'avg_score': round(avg_score, 1) if avg_score else 0
    }
    
    return render_template('reports/monthly_summary.html', stats=stat_summary)

@reports_bp.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    """
    Schedule an appointment route.
    """
    if request.method == 'POST':
        appointment_time_str = request.form.get('appointment_time')
        
        if not appointment_time_str:
            flash('Please select a valid date and time.', 'danger')
            return redirect(url_for('reports.appointment'))
            
        try:
            appointment_datetime = datetime.strptime(appointment_time_str, '%Y-%m-%dT%H:%M')
            if appointment_datetime < datetime.now():
                 flash('Cannot schedule appointments in the past.', 'warning')
                 return redirect(url_for('reports.appointment'))
                 
            user_email = current_user.email
            # Pass the selected time to the helper function
            success, message = schedule_appointment_event(user_email, appointment_datetime)
            
            if success:
                flash(f'Appointment scheduled for {appointment_datetime.strftime("%Y-%m-%d %H:%M")}! Check your calendar (link: {message})', 'success')
            else:
                flash(f'Failed to schedule appointment: {message}', 'danger')
        except ValueError:
             flash('Invalid date format.', 'danger')
             
        return redirect(url_for('dashboard.index'))
    return render_template('reports/appointment.html')

error_bp = Blueprint('error', __name__)

@error_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('error/404.html'), 404

@error_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error/500.html'), 500

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def hub():
    """
    Shows list of contacts to chat with based on role.
    """
    contacts = []
    # Normalize role for comparison
    role = current_user.role.lower() if current_user.role else ''

    if role in ['student', 'user']:
        # Can chat with Counselors and Teachers
        contacts = User.query.filter(User.role.in_(['counselor', 'teacher'])).all()
    elif role in ['counselor', 'teacher']:
        # Can chat with Students and Parents
        contacts = User.query.filter(User.role.in_(['student', 'user', 'parent'])).all()
    elif role == 'parent':
        # Can chat with Counselors/Professionals
        contacts = User.query.filter(User.role.in_(['counselor', 'professional'])).all()
    elif role == 'professional':
         contacts = User.query.filter(User.role == 'parent').all()
        
    return render_template('chat/hub.html', contacts=contacts)

@chat_bp.route('/<int:user_id>', methods=['GET', 'POST'])
@login_required
def room(user_id):
    """
    Chat room with a specific user.
    """
    other_user = db.session.get(User, user_id)
    if not other_user:
        flash('User not found.', 'danger')
        return redirect(url_for('chat.hub'))

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            msg = Message(sender_id=current_user.id, receiver_id=user_id, content=content)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('chat.room', user_id=user_id))

    # Fetch History
    messages = Message.query.filter(
        or_(
            (Message.sender_id == current_user.id) & (Message.receiver_id == user_id),
            (Message.sender_id == user_id) & (Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()

    return render_template('chat/room.html', other_user=other_user, messages=messages)

