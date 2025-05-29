from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json, os

app = Flask(__name__)
app.secret_key = 'secret_key'

USERS_FILE = 'users.json'
CARDS_FILE = 'cards.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def save_card(data):
    if os.path.exists(CARDS_FILE):
        with open(CARDS_FILE, 'r') as f:
            cards = json.load(f)
    else:
        cards = []
    cards.append(data)
    with open(CARDS_FILE, 'w') as f:
        json.dump(cards, f, indent=4)
from flask import render_template

@app.route('/admin', methods=['GET'])
def admin_panel():
    if 'username' not in session or session['username'] != 'admin':
        return 'Bạn không có quyền truy cập!', 403

    if os.path.exists(CARDS_FILE):
        with open(CARDS_FILE, 'r') as f:
            cards = json.load(f)
    else:
        cards = []

    return render_template('admin.html', cards=cards)

@app.route('/admin/approve', methods=['POST'])
def approve_card():
    if 'username' not in session or session['username'] != 'admin':
        return 'Không có quyền!', 403

    username = request.form['username']
    amount = int(request.form['amount'])
    serial = request.form['serial']
    code = request.form['code']

    # Xử lý cộng kim cương
    users = load_users()
    if username in users:
        # Giả sử 1000 VNĐ = 10 KC, hoặc bạn có thể điều chỉnh theo bảng mệnh giá
        kc_map = {
            10000: 95,
            20000: 185,
            50000: 215,
            100000: 1745,
            200000: 3900
        }
        kc = kc_map.get(amount, 0)
        users[username]['diamonds'] += kc
        save_users(users)

    # Cập nhật trạng thái thẻ
    with open(CARDS_FILE, 'r') as f:
        cards = json.load(f)

    for card in cards:
        if card['serial'] == serial and card['code'] == code:
            card['status'] = 'approved'
            break

    with open(CARDS_FILE, 'w') as f:
        json.dump(cards, f, indent=4)

    return redirect(url_for('admin_panel'))

@app.route('/')
def index():
    if 'username' in session:
        users = load_users()
        username = session['username']
        diamonds = users[username]['diamonds']
        return render_template('home.html', username=username, diamonds=diamonds)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return 'Tài khoản đã tồn tại!'
        users[username] = {'password': password, 'diamonds': 0}
        save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('index'))
        return 'Sai tài khoản hoặc mật khẩu!'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/recharge', methods=['POST'])
def recharge():
    if 'username' not in session:
        return redirect(url_for('login'))

    card_type = request.form['card_type']
    amount = int(request.form['amount'])
    serial = request.form['serial']
    code = request.form['code']
    username = session['username']

    card_data = {
        'username': username,
        'type': card_type,
        'amount': amount,
        'serial': serial,
        'code': code,
        'status': 'pending'
    }

    save_card(card_data)
    return 'Thẻ đã gửi, chờ admin duyệt!'

@app.route('/use_diamonds', methods=['POST'])
def use_diamonds():
    if 'username' not in session:
        return 'Chưa đăng nhập', 401
    users = load_users()
    username = session['username']
    amount = int(request.form['amount'])
    if users[username]['diamonds'] >= amount:
        users[username]['diamonds'] -= amount
        save_users(users)
        return 'OK'
    return 'Không đủ kim cương', 400

# ✅ Route xử lý xác nhận nạp ID game (trừ kim cương)
@app.route('/confirm_recharge', methods=['POST'])
def confirm_recharge():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Bạn chưa đăng nhập.'})

    data = request.get_json()
    game_id = data.get('game_id')
    amount = data.get('amount')

    if not game_id or not amount:
        return jsonify({'success': False, 'message': 'Thiếu thông tin.'})

    if amount < 100:
        return jsonify({'success': False, 'message': 'Tối thiểu 100 kim cương.'})

    users = load_users()
    username = session['username']
    user = users.get(username)

    if user['diamonds'] < amount:
        return jsonify({'success': False, 'message': 'Bạn không đủ kim cương.'})

    # Trừ kim cương thật
    user['diamonds'] -= amount
    save_users(users)

    return jsonify({'success': True})
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render cung cấp PORT qua biến môi trường
    app.run(host='0.0.0.0', port=port)
