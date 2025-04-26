from flask import Blueprint, render_template, session, redirect, url_for, flash
from database import Database

pagos_bp = Blueprint('pagos', __name__, url_prefix='/pagos')
db = Database()

@pagos_bp.route('/validar')
def validar_pagos():
    if 'logged_in' in session and session['role'] == 'admin':
        with db.connect() as conn:
            cur = conn.cursor()
            # Obtener los pagos pendientes
            cur.execute("SELECT id, nombre_completo, correo, comprobante_pago, estado_pago FROM participantes WHERE estado_pago = 'Pendiente'")
            pagos_pendientes = cur.fetchall()
            return render_template('admin/validar_pagos.html', pagos_pendientes=pagos_pendientes)
    return redirect(url_for('login.home'))

@pagos_bp.route('/aprobar/<int:id>', methods=["POST"])
def aprobar_pago(id):
    if 'logged_in' in session and session['role'] == 'admin':
        with db.connect() as conn:
            cur = conn.cursor()
            # Aprobar el pago
            cur.execute("UPDATE participantes SET estado_pago = 'Validado' WHERE id = ?", (id,))
            conn.commit()
            flash("Pago aprobado exitosamente.", "success")
            return redirect(url_for('pagos.validar_pagos'))

@pagos_bp.route('/rechazar/<int:id>', methods=["POST"])
def rechazar_pago(id):
    if 'logged_in' in session and session['role'] == 'admin':
        with db.connect() as conn:
            cur = conn.cursor()
            # Rechazar el pago
            cur.execute("UPDATE participantes SET estado_pago = 'Rechazado' WHERE id = ?", (id,))
            conn.commit()
            flash("Pago rechazado.", "danger")
            return redirect(url_for('pagos.validar_pagos'))