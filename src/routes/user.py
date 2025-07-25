from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from src.db import get_all_users, get_user_by_id, insert_user, update_user, delete_user
import uuid

bp = Blueprint('user', __name__)

def is_logged_in():
    return 'user_id' in session

@bp.route('/profil')
def profil():
    if not is_logged_in():
        return redirect(url_for('auth.login'))
    user = get_user_by_id(session['user_id'])
    if not user:
        flash('User tidak ditemukan', 'error')
        return redirect(url_for('auth.login'))
    return render_template('profil.html', title="Profil", user=user)

@bp.route('/manajemen-user')
def manajemen_user():
    if not is_logged_in() or session.get('status') != 'admin':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('dashboard.dashboard'))
    user_list = get_all_users()
    return render_template('manajemen_user.html', title="Manajemen User", user_list=user_list)

@bp.route('/user/tambah', methods=['GET', 'POST'])
def input_user():
    if not is_logged_in() or session.get('status') != 'admin':
        flash('Akses hanya untuk admin.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        nama_lengkap = request.form['nama_lengkap']
        username = request.form['username']
        password = request.form['password']
        status = request.form['status']

        insert_user({
            'nama_lengkap': nama_lengkap,
            'username': username,
            'password': password,
            'status': status
        })
        flash('User berhasil ditambahkan.', 'success')
        return redirect(url_for('user.manajemen_user'))

    return render_template('input_user.html', title='Input User')


@bp.route('/user/edit/<id>', methods=['GET', 'POST'])
def edit_user(id):
    if not is_logged_in() or session.get('status') != 'admin':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('dashboard.dashboard'))

    user = get_user_by_id(id)
    if not user:
        flash('User tidak ditemukan', 'error')
        return redirect(url_for('user.manajemen_user'))

    if request.method == 'POST':
        updated_user = {
            'nama_lengkap': request.form['nama'],
            'username': request.form['username'],
            'email': request.form['email'],
            'password': request.form['password'],
            'status': request.form['status']
        }
        update_user(id, updated_user)
        flash('User berhasil diperbarui', 'success')
        return redirect(url_for('user.manajemen_user'))

    return render_template('edit_user.html', title="Edit User", user=user)

@bp.route('/user/hapus/<id>', methods=['POST'])
def hapus_user(id):
    if not is_logged_in() or session.get('status') != 'admin':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('dashboard.dashboard'))
    delete_user(id)
    flash('User berhasil dihapus', 'success')
    return redirect(url_for('user.manajemen_user'))
