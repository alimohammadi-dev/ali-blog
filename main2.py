from werkzeug.security import generate_password_hash, check_password_hash


password="ali440022"


hashed_pass = generate_password_hash(password, method='pbkdf2', salt_length=8)
print(check_password_hash(password,hashed_pass))