from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.db import (
    fetch_all_balita,
    fetch_balita_by_id,
    insert_balita,
    insert_pengukuran,
    fetch_pengukuran_by_balita_id,
    get_pengukuran_by_id,
    delete_pengukuran_by_id,
)
from src.knn_model import predict_gizi_status, hitung_umur_bulan

bp = Blueprint('anak', __name__)

@bp.route('/data-anak')
def data_anak():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    search = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))
    per_page = 25

    all_anak = fetch_all_balita()
    anak_filtered = [
        a for a in all_anak
        if search in a['nama_anak'].lower()
        or search in str(a['nik'])
        or search in a['alamat'].lower()
    ] if search else all_anak

    total_data = len(anak_filtered)
    total_pages = (total_data + per_page - 1) // per_page
    start_index = (page - 1) * per_page
    anak_list = anak_filtered[start_index: start_index + per_page]

    return render_template(
        'data_anak.html',
        title="Data Anak",
        anak_list=anak_list,
        search=search,
        current_page=page,
        total_pages=total_pages
    )

@bp.route('/input-anak', methods=['GET', 'POST'])
def input_anak():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            nik = request.form['nik']
            nama = request.form['nama']
            alamat = request.form['alamat']
            jenis_kelamin = request.form['jenis_kelamin']
            tanggal_lahir_raw = request.form['tanggal_lahir']
            nama_orang_tua = request.form['nama_orang_tua']

            from datetime import datetime
            tanggal_lahir = datetime.strptime(tanggal_lahir_raw, "%Y-%m-%d").strftime("%d/%m/%Y")

            new_data = {
                "nik": nik,
                "nama": nama,
                "alamat": alamat,
                "jenis_kelamin": jenis_kelamin,
                "tanggal_lahir": tanggal_lahir,
                "nama_orang_tua": nama_orang_tua
            }

            insert_balita(new_data)
            flash("Data anak berhasil ditambahkan!", "success")
            return redirect(url_for('anak.data_anak'))

        except Exception as e:
            flash(f"Gagal menyimpan data anak: {e}", "danger")
            return redirect(url_for('anak.input_anak'))

    return render_template('input_anak.html', title="Input Data Anak")

@bp.route('/input-pengukuran/<int:id>', methods=['GET', 'POST'])
def input_pengukuran(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    anak = fetch_balita_by_id(id)
    if not anak:
        flash('Data anak tidak ditemukan!', 'danger')
        return redirect(url_for('anak.data_anak'))

    if request.method == 'POST':
        try:
            berat = float(request.form['berat_badan'])
            tinggi = float(request.form['tinggi_badan'])
            bulan = request.form['bulan'].strip()
            catatan = request.form.get('catatan_gizi', '')

            if berat <= 0 or tinggi <= 0:
                flash('Berat dan tinggi badan harus lebih dari 0.', 'warning')
                return redirect(url_for('anak.input_pengukuran', id=id))

            umur_bulan = hitung_umur_bulan(anak['tgl_lahir'], bulan)

            if umur_bulan < 0:
                flash('Bulan pengukuran tidak valid.', 'warning')
                return redirect(url_for('anak.input_pengukuran', id=id))

            status_gizi = predict_gizi_status(umur_bulan, berat, tinggi, anak['jenis_kelamin'])

            if 'confirm' in request.form:
                insert_pengukuran({
                    "bulan": bulan,
                    "berat": berat,
                    "tinggi": tinggi,
                    "balita_id": id,
                    "user_id": session['user_id'],
                    "status": status_gizi,
                    "catatan_gizi": catatan
                })


                # Tambahkan ini:
                from src.db import update_status_gizi_balita
                update_status_gizi_balita(id, status_gizi)

                flash(f"pengukuran berhasil disimpan. Status gizi: {status_gizi}", "success")
                return redirect(url_for('anak.detail_anak', id=id))


            return render_template(
                'preview_pengukuran.html',
                title="Konfirmasi pengukuran",
                anak=anak,
                berat=berat,
                tinggi=tinggi,
                umur=umur_bulan,
                bulan=bulan,
                status=status_gizi,
                catatan=catatan
            )

        except ValueError:
            flash("Berat dan tinggi badan harus berupa angka.", "danger")
        except Exception as e:
            flash(f"Terjadi kesalahan: {e}", "danger")

        return redirect(url_for('anak.input_pengukuran', id=id))

    return render_template('input_pengukuran.html', title="Input pengukuran", anak=anak)
from datetime import datetime

@bp.route('/detail-anak/<int:id>')
def detail_anak(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    anak = fetch_balita_by_id(id)
    if not anak:
        abort(404, "Anak tidak ditemukan")

    pengukuran_raw = fetch_pengukuran_by_balita_id(id)

    bulan_map = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4,
        'MEI': 5, 'JUN': 6, 'JUL': 7, 'AGS': 8,
        'SEP': 9, 'OKT': 10, 'NOV': 11, 'DES': 12
    }

    pengukuran_list = []
    for p in pengukuran_raw:
        try:
            berat = float(p['berat'])
            tinggi = float(p['tinggi'])
            if berat == 0 or tinggi == 0:
                continue
        except:
            continue

        bulan_input = (p['bulan'] or "").upper()
        if "_" in bulan_input:
            year, month_abbr = bulan_input.split("_", 1)
            month_num = bulan_map.get(month_abbr, 0)
        else:
            year = "-"
            month_abbr = "-"
            month_num = 0

        pengukuran_list.append({
            **p,
            'bulan': month_abbr,
            'tahun': year,
            'status': p.get('status', 'Belum Diketahui'),
            'petugas_nama': p.get('petugas_nama', 'Tidak diketahui'),
            'sort_key': int(f"{year}{month_num:02}") if year != "-" and month_num > 0 else 0
        })

    pengukuran_list.sort(key=lambda x: x['sort_key'], reverse=True)

    return render_template(
        'detail_anak.html',
        title="Detail Anak",
        anak=anak,
        pengukuran_list=pengukuran_list
    )

@bp.route('/edit-anak/<int:id>', methods=['GET', 'POST'])
def edit_anak(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    anak = fetch_balita_by_id(id)
    if not anak:
        flash("Data anak tidak ditemukan!", "danger")
        return redirect(url_for('anak.data_anak'))

    if request.method == 'POST':
        try:
            anak['nik'] = request.form['nik']
            anak['nama_anak'] = request.form['nama']
            anak['alamat'] = request.form['alamat']
            anak['jenis_kelamin'] = request.form['jenis_kelamin']
            anak['nama_orang_tua'] = request.form['nama_orang_tua']

            tanggal_lahir_raw = request.form['tanggal_lahir']  # yyyy-mm-dd
            from datetime import datetime
            anak['tgl_lahir'] = datetime.strptime(tanggal_lahir_raw, "%Y-%m-%d").strftime("%d/%m/%Y")

            from src.db import update_balita
            update_balita(id, anak)

            flash("Data anak berhasil diperbarui!", "success")
            return redirect(url_for('anak.data_anak'))

        except Exception as e:
            flash(f"Terjadi kesalahan saat mengedit data: {e}", "danger")
            return redirect(url_for('anak.edit_anak', id=id))

    # Konversi tgl_lahir ke yyyy-mm-dd untuk form input
    from datetime import datetime
    try:
        tgl_obj = datetime.strptime(anak['tgl_lahir'], "%d/%m/%Y")
        anak['tgl_lahir_html'] = tgl_obj.strftime("%Y-%m-%d")
    except:
        anak['tgl_lahir_html'] = ""

    return render_template("edit_anak.html", title="Edit Anak", anak=anak)

@bp.route('/pengukuran/<int:id>/delete', methods=['POST'])
def delete_pengukuran(id):
    pengukuran = get_pengukuran_by_id(id)
    if not pengukuran:
        flash('Data tidak ditemukan.', 'danger')
        return redirect(request.referrer or url_for('dashboard.dashboard'))

    delete_pengukuran_by_id(id)
    flash('Data pengukuran berhasil dihapus.', 'success')
    return redirect(request.referrer or url_for('dashboard.dashboard'))
