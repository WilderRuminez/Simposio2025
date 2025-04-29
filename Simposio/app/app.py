from flask import Flask, send_from_directory, url_for, jsonify
from flask_mail import Mail
from database import Database
import os
import qrcode
# Inicializar la aplicación Flask
app = Flask(__name__, template_folder='templates')

# Configuración de la clave secreta
app.secret_key = 'default_secret_key'

# Configuración de la carpeta de subida
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads/pagos')

# Instancia de la base de datos
db = Database()

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'adoniasruminez26@gmail.com'
app.config['MAIL_PASSWORD'] = '123456789'                             
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Registrar los módulos de rutas
from routes.login import login_bp
from routes.admin import admin_bp
from routes.usuario import usuario_bp
from routes.registro import registro_bp
from routes.checkin import checkin_bp
from routes.pagos import pagos_bp

app.register_blueprint(login_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(registro_bp)
app.register_blueprint(checkin_bp)
app.register_blueprint(pagos_bp)

# Ruta para servir los archivos de la carpeta de pagos
@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'uploads/pagos'), filename)

# Ruta para obtener un comprobante de pago por ID
@app.route('/get_comprobante/<int:id>', methods=['GET'])
def get_comprobante(id):
    with db.connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT comprobante_pago FROM participantes WHERE id = ?", (id,))
        result = cur.fetchone()
        if result:
            filename = result[0]
            # Usa la ruta completa relativa a la aplicación
            return send_from_directory('uploads/pagos', filename, as_attachment=False)
        else:
            return jsonify({'error': 'Comprobante no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)