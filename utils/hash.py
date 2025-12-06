from werkzeug.security import generate_password_hash

password = "123456"
hashed_pw = generate_password_hash(password)
print(hashed_pw)
