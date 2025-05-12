from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Global hafıza (ephemeral storage)
users = {}  
# users formatı: { username: {"id": user_id, "password": password} }
next_user_id = 1

carts = {}  
# carts formatı: { user_id: [ { 'name': ..., 'price': ..., 'image': ..., 'quantity': ... }, ... ] }

@app.route('/')
def index():
    return render_template('giriş_yap.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    global next_user_id
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Eğer kullanıcı zaten varsa hata dönelim
        if username in users:
            return "Kullanıcı zaten mevcut", 400
        user_id = next_user_id
        next_user_id += 1
        users[username] = { "id": user_id, "password": password }
        carts[user_id] = []  # boş sepet
        session['user_id'] = user_id
        session['username'] = username
        return redirect(url_for('ev'))
    return render_template('kayıt_ol.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username]["password"] == password:
            session['user_id'] = users[username]["id"]
            session['username'] = username
            return redirect(url_for('ev'))
        else:
            return "Kimlik Bilgileri Geçersiz", 401
    return render_template('giriş_yap.html')

@app.route('/ev')
def ev():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('ev.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    print("Form Data Received:", request.form) # <-- DEBUG PRINT
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    product_name = request.form.get('name')
    product_price = float(request.form.get('price'))
    product_image = request.form.get('image')
    quantity = int(request.form.get('quantity', 1))
    
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    product_name_to_remove = request.form.get('product_name')

    cart = carts.get(user_id, [])

    # Ürünü listeden bul ve sil (sadece ilk eşleşeni siler)
    new_cart = [item for item in cart if item['name'] != product_name_to_remove]

    # Veya miktarı azaltmak isterseniz:
    # for item in cart:
    #     if item['name'] == product_name_to_remove:
    #         item['quantity'] -= 1
    #         if item['quantity'] <= 0:
    #             cart.remove(item) # Miktar 0 ise tamamen kaldır
    #         break 

    carts[user_id] = new_cart # Güncellenmiş sepeti kaydet

    return redirect(url_for('sepet')) # Sepet sayfasına geri yönlendir


    cart = carts.get(user_id, [])
    # Eğer ürün zaten eklenmişse, miktarı arttır
    for item in cart:
        if item['name'] == product_name:
            item['quantity'] += quantity
            break
    else:
        cart.append({
            'name': product_name,
            'price': product_price,
            'image': product_image,
            'quantity': quantity
        })
    carts[user_id] = cart
    return redirect(url_for('ev'))

@app.route('/sepet')
def sepet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    cart = carts.get(user_id, [])
    return render_template('sepet.html', cart=cart)

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if 'user_id' not in session:
        return redirect(url_for('ev'))
    user_id = session['user_id']
    if request.method == 'POST':
        # Ödeme işlemi sonrası, sepeti temizle
        carts[user_id] = []
        return redirect(url_for('ev'))
    return render_template('satın_al.html')

if __name__ == '__main__':
    app.run(debug=True)