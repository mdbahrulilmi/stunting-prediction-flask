dummy_users = [
    {"id": 1, "username": "admin", "password": "admin123", "nama_lengkap": "Administrator", "role": "admin"},
    {"id": 2, "username": "petugas", "password": "petugas123", "nama_lengkap": "Petugas A", "role": "petugas"},
]

def get_user_by_username(username):
    return next((u for u in dummy_users if u['username'] == username), None)
