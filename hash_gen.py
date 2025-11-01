import bcrypt

pwd = "admin123".encode()  # можно заменить на свой пароль
print(bcrypt.hashpw(pwd, bcrypt.gensalt()).decode())
