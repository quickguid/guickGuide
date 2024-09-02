from flask import Blueprint, render_template, request, flash, redirect, url_for, session,jsonify
from .models import User 
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   
from flask_login import login_user, login_required, logout_user, current_user
import uuid

auth = Blueprint('auth', __name__)

ACCESS = {
    'guest': 0,
    'user': 1,
    'admin': 2
}

def generate_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                if user.access in [ACCESS['user'], ACCESS['guest']]:
                    generate_session_id()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'redirect': url_for('views.lesson'), 'category': 'success'})
                    return redirect(url_for('views.lesson'))
                elif user.access == ACCESS['admin']:
                    generate_session_id()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({'redirect': url_for('views.admin_dashboard'), 'category': 'success'})
                    return redirect(url_for('views.admin_dashboard'))
                else:
                    message = 'Your account is not activated, try again.'
            else:
                message = 'Incorrect password, try again.'
        else:
            message = 'Email does not exist.'

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': message, 'category': 'error'})

        flash(message, category='error')

    return render_template("index.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('session_id', None)  # Clear the session ID on logout
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        if user:
            message = 'Email already exists.'
            category = 'error'
        elif len(email) < 4:
            message = 'Email must be greater than 3 characters.'
            category = 'error'
        elif len(first_name) < 2:
            message = 'First name must be greater than 1 character.'
            category = 'error'
        elif password1 != password2:
            message = 'Passwords don\'t match.'
            category = 'error'
        elif len(password1) < 7:
            message = 'Password must be at least 7 characters.'
            category = 'error'
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            message = 'Account created!'
            category = 'success'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': message, 'category': category})
        
        flash(message, category=category)

    return render_template("index.html", user=current_user)

