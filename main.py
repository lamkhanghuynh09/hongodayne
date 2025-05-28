from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
USER_FILE = 'users.json'

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/')
def index():
    show_register = request.args.get('register') == '1'
    message = request.args.get('msg', '')
    return render_template('index.html', message=message, show_register=show_register)

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    users = load_users()
    if username in users:
        return redirect(url_for('index', register=1, msg='Tên đã tồn tại!'))
    users[username] = password
    save_users(users)
    return redirect(url_for('index', msg='Đăng ký thành công!'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    users = load_users()
    if users.get(username) == password:
        return f'Chào mừng, {username}!'
    return redirect(url_for('index', msg='Sai tài khoản hoặc mật khẩu'))
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render cung cấp PORT qua biến môi trường
    app.run(host='0.0.0.0', port=port)
