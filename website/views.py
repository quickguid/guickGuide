from flask import Blueprint, flash
from flask_login import login_required, current_user
from flask import  flash, redirect, url_for, request
from flask_login import current_user,  login_required
from functools import wraps
from flask import render_template
from flask import  request, jsonify
from .models import UserAction, ACCESS, Lesson, UserAction
from .auth import session
from . import db
from datetime import datetime

views = Blueprint('views', __name__)

### custom wrap to determine access level ###
def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated: #the user is not logged in
                return redirect(url_for('login'))
            #user = User.query.filter_by(id=current_user.id).first()
            if not current_user.allowed(access_level):
                flash('You do not have access to this resource.', 'Error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@views.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@views.route('/lessons', methods=['GET'])
@login_required
def lesson():
    lessons = Lesson.query.limit(2).all()
    return render_template("lessons.html", lessons=lessons)


@views.route('/admin')
@requires_access_level(ACCESS['admin']) 
@login_required
def admin_dashboard():
    actions_data = db.session.query(UserAction).all()
    return render_template('admin.html', actions_data=actions_data)


@views.route('/submit', methods=['POST'])
@login_required
def submit():
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    action_id = data.get('action_id')
    time_clicked_str = data.get('time_clicked')
    time_clicked = datetime.strptime(time_clicked_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    user_id = current_user.id
    session_id = session.get('session_id')
    user_action = UserAction(user_id=user_id, session_id=session_id, lesson_id=lesson_id, action_id=action_id, time_clicked=time_clicked)
    db.session.add(user_action)
    db.session.commit()
    # Return a response
    return jsonify({'status': 'success', 'lesson_id': lesson_id, 'action_id': action_id, 'time_clicked': time_clicked})

@views.route('/lessons/<item_id>')
@login_required
def show_lessons(item_id):
    # Fetch the lesson from the database based on item_id
    lesson = Lesson.query.get(item_id)
    return render_template('show_lesson.html', lesson=lesson)


@views.route('/get_user_actions/<int:user_id>')
@login_required
@requires_access_level(ACCESS['admin'])
def get_user_actions(user_id):
    user_actions = db.session.query(UserAction).filter_by(user_id=user_id).all()
    
    # Convert the actions to a list of dictionaries
    actions_data = [{
        'user_id': action.user_id,
        'session_id': action.session_id,
        'lesson_id': action.lesson_id,
        'action_id': action.action_id,
        'time_clicked': action.time_clicked.strftime('%Y-%m-%d %H:%M:%S')  # Formatting datetime to string
    } for action in user_actions]
    
    return jsonify(actions_data)

@views.route('/get_all_actions')
@login_required
@requires_access_level(ACCESS['admin'])
def get_all_actions():
    all_actions = db.session.query(UserAction).all()
    
    actions_data = [{
        'user_id': action.user_id,
        'session_id': action.session_id,
        'lesson_id': action.lesson_id,
        'action_id': action.action_id,
        'time_clicked': action.time_clicked.strftime('%Y-%m-%d %H:%M:%S')
    } for action in all_actions]
    
    return jsonify(actions_data)


