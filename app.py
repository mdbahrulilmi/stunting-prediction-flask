from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "rahasia_super_secret"

# ----------------------
# Dummy Data
# ----------------------
dummy_users = [
    {"id": 1, "username": "admin", "password": "admin123", "nama_lengkap": "Administrator", "role": "admin"},
    {"id": 2, "username": "petugas", "password": "petugas123", "nama_lengkap": "Petugas A", "role": "petugas"},
]

dummy_anak = [
    {"id": 1, "nama": "Budi", "nik": "1234567890123456", "alamat": "Jl. Merdeka 1", "jenis_kelamin": "L", "tanggal_lahir": "2020-01-01", "nama_orang_tua": "Pak Andi"},
    {"id": 2, "nama": "Siti", "nik": "6543210987654321", "alamat": "Jl. Melati 5", "jenis_kelamin": "P", "tanggal_lahir": "2021-05-15", "nama_orang_tua": "Bu Dewi"},
]

dummy_pemeriksaan = [
    {"id": 1, "anak_id": 1, "berat_badan": 10.5, "tinggi_badan": 70, "bulan_pemeriksaan": 6, "tahun_pemeriksaan": 2023, "catatan_gizi": "Perlu vitamin A", "status_stunting": "Normal", "petugas_id": 2},
    {"id": 2, "anak_id": 2, "berat_badan": 8.5, "tinggi_badan": 65, "bulan_pemeriksaan": 7, "tahun_pemeriksaan": 2023, "catatan_gizi": "Stunting ringan", "status_stunting": "Stunting", "petugas_id": 2},
]

# ----------------------
# Helper Functions
# ----------------------
def get_user_by_username(username):
    return next((u for u in dummy_users if u['username'] == username), None)

def get_anak_by_id(anak_id):
    return next((a for a in dummy_anak if a['id'] == anak_id), None)

def get_pemeriksaan_by_anak(anak_id):
    return [p for p in dummy_pemeriksaan if p['anak_id'] == anak_id]

def next_anak_id():
    return max(a['id'] for a in dummy_anak) + 1 if dummy_anak else 1

def next_pemeriksaan_id():
    return max(p['id'] for p in dummy_pemeriksaan) + 1 if dummy_pemeriksaan else 1

# ----------------------
# Routes
# ----------------------
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['nama_lengkap'] = user['nama_lengkap']
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        flash('Username atau password salah', 'error')
    return render_template('login.html', title='Login')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout berhasil', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    total_anak = len(dummy_anak)
    anak_stunting = sum(1 for p in dummy_pemeriksaan if p['status_stunting'] == 'Stunting')
    anak_normal = total_anak - anak_stunting

    return render_template('dashboard.html',
                           title="Dashboard",
                           total_anak=total_anak,
                           anak_stunting=anak_stunting,
                           anak_normal=anak_normal)

@app.route('/data-anak')
def data_anak():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '')
    if search:
        anak_list = [a for a in dummy_anak if search.lower() in a['nama'].lower() or search in a['nik']]
    else:
        anak_list = dummy_anak

    return render_template('data_anak.html', title="Data Anak", anak_list=anak_list, search=search)

@app.route('/input-anak', methods=['GET', 'POST'])
def input_anak():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_anak = {
            "id": next_anak_id(),
            "nama": request.form['nama'],
            "nik": request.form['nik'],
            "alamat": request.form['alamat'],
            "jenis_kelamin": request.form['jenis_kelamin'],
            "tanggal_lahir": request.form['tanggal_lahir'],
            "nama_orang_tua": request.form['nama_orang_tua']
        }
        dummy_anak.append(new_anak)
        flash('Data anak berhasil ditambahkan!', 'success')
        return redirect(url_for('data_anak'))

    return render_template('input_anak.html', title="Input Data Anak")

@app.route('/input-pemeriksaan/<int:id>', methods=['GET', 'POST'])
def input_pemeriksaan(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    anak = get_anak_by_id(id)
    if not anak:
        flash('Data anak tidak ditemukan!', 'error')
        return redirect(url_for('data_anak'))

    if request.method == 'POST':
        new_pemeriksaan = {
            "id": next_pemeriksaan_id(),
            "anak_id": anak['id'],
            "berat_badan": float(request.form['berat_badan']),
            "tinggi_badan": float(request.form['tinggi_badan']),
            "tahun_pemeriksaan": int(request.form['tahun_pemeriksaan']),
            "bulan_pemeriksaan": int(request.form['bulan_pemeriksaan']),
            "catatan_gizi": request.form.get('catatan_gizi', ''),
            "status_stunting": "Stunting" if float(request.form['tinggi_badan']) < 65 else "Normal",
            "petugas_id": session['user_id']
        }
        dummy_pemeriksaan.append(new_pemeriksaan)
        flash('Pemeriksaan berhasil ditambahkan!', 'success')
        return redirect(url_for('detail_anak', id=anak['id']))

    return render_template('input_pemeriksaan.html', title="Input Pemeriksaan", anak=anak)

@app.route('/detail-anak/<int:id>')
def detail_anak(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    anak = get_anak_by_id(id)
    if not anak:
        flash('Data anak tidak ditemukan!', 'error')
        return redirect(url_for('data_anak'))

    pemeriksaan_list = get_pemeriksaan_by_anak(id)
    return render_template('detail_anak.html', title="Detail Anak", anak=anak, pemeriksaan_list=pemeriksaan_list)

@app.route('/profil')
def profil():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = next(u for u in dummy_users if u['id'] == session['user_id'])
    return render_template('profil.html', title="Profil", user=user)

@app.route('/manajemen-user')
def manajemen_user():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('dashboard'))
    return render_template('manajemen_user.html', title="Manajemen User", user_list=dummy_users)

if __name__ == "__main__":
    app.run(debug=True)
