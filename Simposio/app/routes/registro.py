import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import Database
from werkzeug.security import generate_password_hash

db = Database()

upload_folder = 'app/uploads/pagos'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

# Definición de la ruta y el blueprint para el módulo de registro
ALLOWED_EXTENSIONS = {'pdf'}  # Solo se permite PDF
registro_bp = Blueprint('registro', __name__, url_prefix='/registro')

# Verifica si el archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@registro_bp.route('/')
def registro_home():
    return render_template('login/registro.html')

@registro_bp.route('/crear', methods=["POST"])
def crear_registro():
    nombre = request.form['txtNombre']
    correo = request.form['txtCorreo']
    telefono = request.form['txtTelefono']
    empresa = request.form['txtEmpresa']
    tipo_participante = request.form['txtTipoParticipante']
    carnet = request.form.get('txtCarnet')  # Puede ser None si no es estudiante
    password = request.form['txtPassword']
    archivo = request.files['comprobante']

    # Validar que el carnet sea obligatorio para estudiantes
    if tipo_participante == "Estudiante" and not carnet:
        flash("El campo 'Carnet' es obligatorio para estudiantes.", "danger")
        return redirect(url_for('registro.registro_home'))

    # Cifrar la contraseña
    hashed_password = generate_password_hash(password)

    # Validar el archivo
    if archivo and allowed_file(archivo.filename):
        filename = secure_filename(archivo.filename)
        archivo.save(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads/pagos', filename))

        try:
            with db.connect() as conn:
                cur = conn.cursor()
                # Insertar el nuevo participante con el rol `2` (staff)
                cur.execute("""
                    INSERT INTO participantes (nombre_completo, correo, telefono, empresa, tipo_participante, carnet, pass, comprobante_pago, id_rol)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nombre, correo, telefono, empresa, tipo_participante, carnet, hashed_password, filename, 2))
                conn.commit()
                flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
                return redirect(url_for('registro.registro_home'))
        except Exception as e:
            flash("Error al registrar: " + str(e), "danger")
            return redirect(url_for('registro.registro_home'))
    else:
        flash("Archivo inválido. Solo se permiten archivos PDF.", "danger")
        return redirect(url_for('registro.registro_home'))

@registro_bp.route('/comprobante/<filename>')
def ver_comprobante(filename):
    try:
        return redirect(url_for('uploads', filename=filename))
    except Exception as e:
        flash("Error al obtener el comprobante: " + str(e), "danger")
        return redirect(url_for('registro.registro_home'))