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


@views.route('/lessons', methods=['GET'])
@login_required
def lesson():
    lessons = Lesson.query.all()
    return render_template("lessons.html", lessons=lessons)

@views.route('/lesson/<int:lesson_id>', methods=['GET'])
@login_required
def show_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template("show_lesson.html", lesson=lesson)

    
@requires_access_level(ACCESS['admin']) 
@views.route('/admin')
def admin_dashboard():
    # Query to get the count of each action_id
    action_counts = db.session.query(
        UserAction.action_id,
        db.func.count(UserAction.id).label('count')
    ).group_by(UserAction.action_id).all()

    return render_template('admin.html', action_counts=action_counts)


@views.route('/submit', methods=['POST'])
@login_required
def submit():
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    action_id = data.get('action_id')
    time_clicked_str = data.get('time_clicked')
    time_clicked = datetime.strptime(time_clicked_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    user_id = current_user.id
    session_id = session.get('session_id', 'No session ID found')
    user_action = UserAction(user_id=user_id, session_id=session_id, lesson_id=lesson_id, action_id=action_id, time_clicked=time_clicked)
    db.session.add(user_action)
    db.session.commit()

    # Return a response
    return jsonify({'status': 'success', 'lesson_id': lesson_id, 'action_id': action_id, 'time_clicked': time_clicked})
