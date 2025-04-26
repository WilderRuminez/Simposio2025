from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database import Database
from werkzeug.security import check_password_hash

db = Database()

login_bp = Blueprint('login', __name__)

@login_bp.route('/')
def home():
    return render_template('login/index.html')

@login_bp.route('/acceso-login', methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']
        
        # Para depuración
        print(f"Intento de login para: {_correo}")

        with db.connect() as conn:
            if conn:
                cur = conn.cursor()

                # Verificar si el correo existe en la tabla `usuarios` (administradores y staff)
                cur.execute("SELECT id, correo, id_rol, pass FROM usuarios WHERE correo = ?", (_correo,))
                user = cur.fetchone()

                if user:
                    user_id, correo, id_rol, hashed_password = user
                    print(f"Usuario encontrado en tabla 'usuarios', rol: {id_rol}")

                    # Verificar la contraseña
                    if check_password_hash(hashed_password, _password):
                        session.clear()  # Limpiar cualquier sesión existente
                        session['logged_in'] = True
                        session['user_id'] = user_id
                        session['email'] = correo
                        session['role'] = 'admin' if id_rol == 1 else 'staff'
                        
                        print(f"Login exitoso, rol asignado: {session['role']}")

                        # Redirigir según el rol
                        if session['role'] == 'admin':
                            print("Redirigiendo a admin.admin_home")
                            return redirect(url_for('admin.admin_home'))
                        else:
                            print("Redirigiendo a usuario.usuario_home")
                            return redirect(url_for('usuario.usuario_home'))
                    else:
                        flash("Contraseña incorrecta.", "danger")
                        return redirect(url_for('login.home'))

                # Si no está en `usuarios`, verificar en la tabla `participantes`
                cur.execute("SELECT id, correo, id_rol, estado_pago, pass FROM participantes WHERE correo = ?", (_correo,))
                participante = cur.fetchone()

                if participante:
                    participante_id, correo, id_rol, estado_pago, hashed_password = participante
                    print(f"Usuario encontrado en tabla 'participantes', estado_pago: {estado_pago}")

                    # Verificar si el estado de pago es "Validado"
                    if estado_pago == "Validado":
                        if check_password_hash(hashed_password, _password):
                            session.clear()  # Limpiar cualquier sesión existente
                            session['logged_in'] = True
                            session['user_id'] = participante_id
                            session['email'] = correo
                            session['role'] = 'staff' if id_rol == 2 else 'participante'
                            
                            print(f"Login exitoso para participante, rol asignado: {session['role']}")
                            print("Redirigiendo a usuario.usuario_home")
                            
                            # Redirigir al panel de usuario
                            return redirect(url_for('usuario.usuario_home'))
                        else:
                            flash("Contraseña incorrecta.", "danger")
                            return redirect(url_for('login.home'))
                    else:
                        flash("Tu pago aún no ha sido validado. Por favor, espera la confirmación.", "warning")
                        return redirect(url_for('login.home'))
                else:
                    flash("Correo no registrado.", "danger")
                    return redirect(url_for('login.home'))
    return render_template('login/index.html')

@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.home'))