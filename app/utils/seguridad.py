import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8') 

def verificar_password(password_plana, password_hashed):
    if isinstance(password_hashed, str):
        password_hashed = password_hashed.encode('utf-8')
    return bcrypt.checkpw(password_plana.encode('utf-8'), password_hashed)

