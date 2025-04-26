from flask import Blueprint, render_template, request, jsonify
from database import Database

checkin_bp = Blueprint('checkin', __name__, url_prefix='/checkin')
db = Database()

# Ruta para la página principal del módulo de Check-In
@checkin_bp.route('/')
def checkin_home():
    return render_template('checkin/checkin.html')

# Ruta para registrar la asistencia
@checkin_bp.route('/registrar', methods=["POST"])
def registrar_asistencia():
    codigo_qr = request.form['codigo_qr']
    with db.connect() as conn:
        cur = conn.cursor()
        # Buscar al participante por su código QR
        cur.execute("SELECT id, asistencia FROM participantes WHERE codigo_qr = ?", (codigo_qr,))
        participante = cur.fetchone()
        if participante:
            # Verificar si ya se registró la asistencia
            if participante[1]:  # Índice 1 corresponde al campo 'asistencia'
                return jsonify({"status": "error", "message": "Asistencia ya registrada"})
            # Registrar asistencia
            cur.execute("UPDATE participantes SET asistencia = 1 WHERE id = ?", (participante[0],))
            conn.commit()
            return jsonify({"status": "success", "message": "Asistencia registrada exitosamente"})
        return jsonify({"status": "error", "message": "Código QR inválido"})