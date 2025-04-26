from werkzeug.security import generate_password_hash

# Contraseñas originales
admin_password = "admin123"
staff_password = "staff123"

# Generar hashes
hashed_admin_password = generate_password_hash(admin_password)
hashed_staff_password = generate_password_hash(staff_password)

# Imprimir los hashes
print(f"Hash para admin123: {hashed_admin_password}")
print(f"Hash para staff123: {hashed_staff_password}")