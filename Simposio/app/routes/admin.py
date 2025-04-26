import qrcode
import os
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from database import Database
from flask_mail import Mail, Message

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
db = Database()
mail = Mail()

@admin_bp.route('/')
def admin_home():
    if 'logged_in' in session and session['role'] == 'admin':
        return render_template('admin/admin.html')
    return redirect(url_for('login.home'))

@admin_bp.route('/validar-pagos')
def validar_pagos():
    if 'logged_in' in session and session['role'] == 'admin':
        with db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre_completo, correo, comprobante_pago, estado_pago FROM participantes WHERE estado_pago = 'Pendiente'")
            pagos_pendientes = cur.fetchall()
            return render_template('admin/validar_pagos.html', pagos_pendientes=pagos_pendientes)
    return redirect(url_for('login.home'))

@admin_bp.route('/aprobar-pago/<int:id>', methods=["POST"])
def aprobar_pago(id):
    with db.connect() as conn:
        cur = conn.cursor()
        # Obtener información del participante
        cur.execute("SELECT correo, nombre_completo FROM participantes WHERE id = ?", (id,))
        participante = cur.fetchone()
        if participante:
            correo, nombre_completo = participante

            # Generar un código QR único
            codigo_qr = f"{id}-{os.urandom(8).hex()}"
            qr = qrcode.make(codigo_qr)
            qr_path = f"app/static/qr_codes/{codigo_qr}.png"
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)  # Crear la carpeta si no existe
            qr.save(qr_path)

            # Actualizar el estado de pago y guardar el código QR en la base de datos
            cur.execute("UPDATE participantes SET estado_pago = 'Validado', codigo_qr = ? WHERE id = ?", (codigo_qr, id))
            conn.commit()

            # Enviar correo con el código QR
            msg = Message("Pago Validado - Código QR", recipients=[correo])
            msg.body = f"Hola {nombre_completo},\n\nTu pago ha sido validado. Por favor, utiliza el siguiente código QR para registrar tu asistencia."
            with open(qr_path, "rb") as qr_file:
                msg.attach(f"{codigo_qr}.png", "image/png", qr_file.read())
            mail.send(msg)

            flash("Pago aprobado exitosamente y correo enviado con el código QR.", "success")
        else:
            flash("Participante no encontrado.", "danger")
    return redirect(url_for('admin.validar_pagos'))

@admin_bp.route('/rechazar-pago/<int:id>', methods=["POST"])
def rechazar_pago(id):
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE participantes SET estado_pago = 'Rechazado' WHERE id = ?", (id,))
        conn.commit()
        flash("Pago rechazado.", "danger")
    return redirect(url_for('admin.validar_pagos'))

@admin_bp.route('/participantes')
def listar_participantes():
    if 'logged_in' in session and session['role'] == 'admin':
        with db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre_completo, correo, telefono, empresa, tipo_participante, estado_pago, asistencia FROM participantes")
            participantes = cur.fetchall()
            return render_template('admin/listar_participantes.html', participantes=participantes)
    return redirect(url_for('login.home'))

@admin_bp.route('/asistencia')
def conteo_asistencia():
    if 'logged_in' in session and session['role'] == 'admin':
        with db.connect() as conn:
            cur = conn.cursor()
            # Total de asistentes
            cur.execute("SELECT COUNT(*) AS total_asistencia FROM participantes WHERE asistencia = 1")
            total_asistencia = cur.fetchone()[0]  # Accede al primer valor de la tupla
            # Total de participantes
            cur.execute("SELECT COUNT(*) AS total_participantes FROM participantes")
            total_participantes = cur.fetchone()[0]  # Accede al primer valor de la tupla
            return render_template('admin/conteo_asistencia.html', total_asistencia=total_asistencia, total_participantes=total_participantes)
    return redirect(url_for('login.home'))