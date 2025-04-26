from flask import Blueprint, render_template, session, redirect, url_for

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuario')

@usuario_bp.route('/')
def usuario_home():
    if 'logged_in' in session and session['role'] in ['staff', 'participante']:
        return render_template('usuario/usuario.html')
    return redirect(url_for('login.home'))
