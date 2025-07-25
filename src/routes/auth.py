from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.db import get_user_by_username

bp = Blueprint('auth', __name__)

@bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['status'] = user['status']  # admin / petugas
            session['nama_lengkap'] = user['nama_lengkap']
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('login.html', title='Login')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logout berhasil.', 'success')
    return redirect(url_for('auth.login'))
