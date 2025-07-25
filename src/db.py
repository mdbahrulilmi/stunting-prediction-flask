from conn import get_connection

def fetch_all_balita():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM balita")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def fetch_balita_by_id(anak_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM balita WHERE id = %s", (anak_id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def insert_balita(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO balita (nik, nama_anak, tgl_lahir, jenis_kelamin, nama_ibu, alamat, status_gizi)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data['nik'],
        data['nama'],
        data['tanggal_lahir'],
        data['jenis_kelamin'],
        data['nama_orang_tua'],
        data['alamat'],
        data.get('status_gizi', 'Tidak Stunting')
    ))
    conn.commit()
    cursor.close()
    conn.close()

def update_balita(id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE balita
        SET nik = %s, nama_anak = %s, alamat = %s, jenis_kelamin = %s, tgl_lahir = %s, nama_ibu = %s
        WHERE id = %s
    """, (
        data['nik'],
        data['nama_anak'],
        data['alamat'],
        data['jenis_kelamin'],
        data['tgl_lahir'],
        data['nama_orang_tua'],
        id
    ))
    conn.commit()
    cursor.close()
    conn.close()

def update_status_gizi_balita(balita_id, status_gizi):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE balita
        SET status_gizi = %s
        WHERE id = %s
    """, (status_gizi, balita_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_pengukuran_by_id(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pengukuran WHERE id = %s", (id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def delete_pengukuran_by_id(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pengukuran WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()


def insert_pengukuran(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pengukuran (bulan, berat, tinggi, balita_id)
        VALUES (%s, %s, %s, %s)
    """, (
        data['bulan'],
        data['berat'],
        data['tinggi'],
        data['balita_id']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_pengukuran_by_balita_id(balita_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, u.nama_lengkap AS petugas_nama
        FROM pengukuran p
        LEFT JOIN users u ON p.user_id = u.id
        WHERE p.balita_id = %s
        ORDER BY bulan DESC
    """, (balita_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def fetch_dataset_pengukuran():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            p.berat, 
            p.tinggi, 
            p.bulan, 
            b.status_gizi AS status, 
            b.tgl_lahir, 
            b.jenis_kelamin
        FROM pengukuran p
        JOIN balita b ON p.balita_id = b.id
        WHERE 
            b.status_gizi IS NOT NULL
            AND p.berat IS NOT NULL AND p.berat != ''
            AND p.tinggi IS NOT NULL AND p.tinggi != ''
            AND b.tgl_lahir IS NOT NULL
            AND b.jenis_kelamin IS NOT NULL
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users ORDER BY nama_lengkap ASC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def insert_user(user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (nama_lengkap, username, password, status)
        VALUES ( %s, %s, %s, %s)
    """, (
        user['nama_lengkap'],
        user['username'],
        user['password'],
        user['status']
    ))
    conn.commit()
    cursor.close()
    conn.close()


def update_user(user_id, user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET nama_lengkap = %s, username = %s, email = %s, password = %s, status = %s
        WHERE id = %s
    """, (
        user['nama_lengkap'],
        user['username'],
        user['email'],
        user['password'],
        user['status'],
        user_id
    ))
    conn.commit()
    cursor.close()
    conn.close()

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
