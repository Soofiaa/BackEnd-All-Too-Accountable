import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verificar_password(password_plana, password_hashed):
    return bcrypt.checkpw(password_plana.encode('utf-8'), password_hashed.encode('utf-8'))
