from flask import Flask, render_template, request, redirect, url_for, session
import json, os

app = Flask(__name__)
app.secret_key = 'supersecret'  # Để dùng session
USER_FILE = 'users.json'

def load_users():
    try:
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def index():
    msg = request.args.get('msg')
    show_register = request.args.get('register') == '1'
    return render_template('index.html', message=msg, show_register=show_register)

@app.route('/register', methods=['POST'])
def register():
    users = load_users()
    username = request.form['username']
    if username in users:
        return redirect(url_for('index', msg='Tên đã tồn tại!', register=1))
    users[username] = {'password': request.form['password'], 'diamonds': 0}
    save_users(users)
    return redirect(url_for('index', msg='Đăng ký thành công!'))

@app.route('/login', methods=['POST'])
def login():
    users = load_users()
    username = request.form['username']
    password = request.form['password']
    user = users.get(username)
    if user and user['password'] == password:
        session['username'] = username
        return redirect(url_for('home'))
    return redirect(url_for('index', msg='Sai tài khoản hoặc mật khẩu'))

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect('/')
    users = load_users()
    username = session['username']
    diamonds = users[username].get('diamonds', 0)
    return render_template('home.html', username=username, diamonds=diamonds)

@app.route('/recharge', methods=['POST'])
def recharge():
    if 'username' not in session:
        return redirect('/')
    users = load_users()
    username = session['username']
    amount = int(request.form['amount'])

    # Nạp thẻ = tặng kim cương
    bonus = amount // 1000
    users[username]['diamonds'] += bonus
    save_users(users)

    return redirect(url_for('home'))
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render cung cấp PORT qua biến môi trường
    app.run(host='0.0.0.0', port=port)
