from flask import Blueprint, render_template, session, redirect, url_for
from src.db import fetch_all_balita

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    all_anak = fetch_all_balita()
    total_anak = len(all_anak)
    anak_stunting = sum(1 for a in all_anak if a['status_gizi'].lower() == 'stunting')
    anak_normal = total_anak - anak_stunting

    return render_template('dashboard.html',
                           title="Dashboard",
                           total_anak=total_anak,
                           anak_stunting=anak_stunting,
                           anak_normal=anak_normal)
