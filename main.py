from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

USERS_FILE = 'users.json'

def read_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def write_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data['username']
    password = data['password']
    users = read_users()

    if username in users:
        return "Tài khoản đã tồn tại!", 409

    users[username] = generate_password_hash(password)
    write_users(users)
    return redirect('/?msg=Đăng ký thành công!')

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data['username']
    password = data['password']
    users = read_users()

    if username in users and check_password_hash(users[username], password):
        return redirect('/?msg=Đăng nhập thành công!')
    else:
        return "Sai tài khoản hoặc mật khẩu", 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
