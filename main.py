from flask import Flask, render_template, request, redirect, session, jsonify
import json, os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USER_FILE = 'users.json'
ADMIN_USERNAME = 'admin'

# Helper functions
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    users = load_users()
    username = request.form['username']
    password = request.form['password']

    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect('/home')
    else:
        return 'Sai tài khoản hoặc mật khẩu'

@app.route('/register', methods=['POST'])
def register():
    users = load_users()
    username = request.form['username']
    password = request.form['password']

    if username in users:
        return 'Tài khoản đã tồn tại'

    users[username] = {'password': password, 'diamonds': 0}
    save_users(users)
    return redirect('/')

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
    
    card_data = {
        'username': session['username'],
        'card_type': request.form['card_type'],
        'amount': request.form['amount'],
        'serial': request.form['serial'],
        'code': request.form['code']
    }

    # Lưu vào file admin duyệt
    with open('pending_cards.json', 'a') as f:
        f.write(json.dumps(card_data) + '\n')

    return 'Đã gửi thẻ thành công, chờ admin duyệt! <a href="/home">Quay lại</a>'

@app.route('/confirm_recharge', methods=['POST'])
def confirm_recharge():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Chưa đăng nhập'})

    data = request.json
    amount = int(data.get('amount', 0))
    username = session['username']

    users = load_users()
    if username not in users:
        return jsonify({'success': False, 'message': 'Tài khoản không tồn tại'})

    diamonds = users[username].get('diamonds', 0)

    if amount < 100:
        return jsonify({'success': False, 'message': 'Tối thiểu phải nạp 100 kim cương'})
    if amount > diamonds:
        return jsonify({'success': False, 'message': 'Không đủ kim cương'})

    users[username]['diamonds'] -= amount
    save_users(users)

    return jsonify({'success': True, 'new_diamonds': users[username]['diamonds']})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render cung cấp PORT qua biến môi trường
    app.run(host='0.0.0.0', port=port)
