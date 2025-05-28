from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecret'  # Để dùng session

USER_FILE = 'users.json'
RECHARGE_FILE = 'recharges.json'

# ========== Helper: Load & Save ==========
def load_users():
    try:
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_recharges():
    try:
        with open(RECHARGE_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_recharges(recharges):
    with open(RECHARGE_FILE, 'w') as f:
        json.dump(recharges, f, indent=4)

# ========== Routes ==========

@app.route('/')
def index():
    msg = request.args.get('msg')
    show_register = request.args.get('register') == '1'
    return render_template('index.html', message=msg, show_register=show_register)

@app.route('/register', methods=['POST'])
def register():
    users = load_users()
    username = request.form['username']
    password = request.form['password']

    if username in users:
        return redirect(url_for('index', msg='Tên đã tồn tại!', register=1))

    users[username] = {
        'password': password,
        'diamonds': 0,
        'role': 'user'
    }
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
        session['role'] = user.get('role', 'user')
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
    username = session['username']
    data = {
        'username': username,
        'card_type': request.form['card_type'],
        'amount': int(request.form['amount']),
        'serial': request.form['serial'],
        'code': request.form['code']
    }
    recharges = load_recharges()
    recharges.append(data)
    save_recharges(recharges)
    return redirect(url_for('home'))

@app.route('/admin')
def admin_panel():
    if 'username' not in session or session.get('role') != 'admin':
        return "⛔️ Bạn không có quyền truy cập", 403

    recharges = load_recharges()
    return render_template('admin.html', recharges=recharges)

@app.route('/approve', methods=['POST'])
def approve():
    if 'username' not in session or session.get('role') != 'admin':
        return "⛔️ Không được phép", 403

    username = request.form['username']
    amount = int(request.form['amount'])

    users = load_users()
    if username in users:
        users[username]['diamonds'] += amount // 1000
        save_users(users)

    # Xoá giao dịch khỏi danh sách
    recharges = load_recharges()
    recharges = [r for r in recharges if not (r['username'] == username and r['amount'] == amount)]
    save_recharges(recharges)

    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render cung cấp PORT qua biến môi trường
    app.run(host='0.0.0.0', port=port)
