from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random, string

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///management.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'

db = SQLAlchemy(app)

class authendication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.String(10), unique=True, nullable=False)
    product_user_id = db.Column(db.String(10), unique=True, nullable=False)
    warehouse_name = db.Column(db.String(10), unique=True, nullable=False)
    warehouse_password = db.Column(db.Integer, unique=False, nullable=False)
    
class product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(10), unique=True, nullable=False)
    product_user_id = db.Column(db.String(10), unique=True, nullable=False)
    product_name = db.Column(db.String(20), unique=False, nullable=False)
    product_amount = db.Column(db.Integer, unique=False, nullable=False)
    product_qty = db.Column(db.Integer, unique=False, nullable=False)
    product_total_amount = db.Column(db.Float, nullable=False) 
    
class RequestProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    warehouse_from_name = db.Column(db.String(100), unique=False, nullable=False)
    warehouse_to_name = db.Column(db.String(100), unique=False, nullable=False)
    warehouse_from_location = db.Column(db.String(50), unique=False, nullable=False)
    warehouse_to_location = db.Column(db.String(50), unique=False, nullable=False)
    
    warehouse_req_product_name = db.Column(db.String(20), unique=False, nullable=False)
    warehouse_req_product_amount = db.Column(db.Integer, unique=False, nullable=False)
    warehouse_req_product_qty = db.Column(db.Integer, unique=False, nullable=False)
    warehouse_req_product_want_qty = db.Column(db.Integer, unique=False, nullable=False)
    
    movment_id = db.Column(db.String(7), unique=True, nullable=False)
    timestamp = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.String(10), unique=False, nullable=False)
    
class ResponseProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    res_movment_id = db.Column(db.String(7), unique=True, nullable=False)
    check_status = db.Column(db.String(10), unique=False, nullable=False)
    
with app.app_context():
    db.create_all()

@app.route("/")
def main():
    return render_template('index.html')

def warehouseid():
    random_number = random.randint(100000, 999999)
    
    product_user_id = f"PUI{random_number}"
    warehouse_id = f"WHI{random_number}"
    
    return product_user_id, warehouse_id

# warehouse Oauthendication
@app.route("/register", methods=['POST', 'GET'])
def Register():
    product_user_id, warehouse_id = warehouseid()
    
    if request.method == 'POST':
        warehouse_name = request.form.get('warehouse_name')
        warehouse_password = request.form.get('warehouse_password')
        
        check_user = authendication.query.filter_by(warehouse_name=warehouse_name).first()
        
        if check_user:
            flash("user name already existing || Please Login", "error")
            return redirect(url_for('Login'))
        
        dataSet = authendication(warehouse_id=warehouse_id, product_user_id=product_user_id, warehouse_name=warehouse_name, warehouse_password=warehouse_password)
        db.session.add(dataSet)
        db.session.commit()
        
        flash("user create successfully", "success")
        return redirect(url_for('Login'))
    return render_template('Oauth/register.html', product_user_id=product_user_id, warehouse_id=warehouse_id)

@app.route("/login", methods=['POST', 'GET'])
def Login():
    if request.method == 'POST':
        warehouse_name = request.form.get('warehouse_name')
        warehouse_password = request.form.get('warehouse_password')
        
        # Check if the user exists in the database
        check_login = authendication.query.filter_by(
            warehouse_name=warehouse_name, warehouse_password=warehouse_password
        ).first()
        
        if not check_login:
            flash("User not registered or incorrect credentials!", "error")
            return redirect(url_for('Register'))
        
        # Store user details in session
        session['user_id'] = check_login.id
        session['warehouse_name'] = check_login.warehouse_name
        
        flash("Login successful!", "success")
        return redirect(url_for('main'))
    
    return render_template('Oauth/login.html')

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        flash("You need to log in first.", "error")
        return redirect(url_for('Login'))
    
    user = session.get('warehouse_name')
    return render_template("profile/profile.html", user=user)

@app.route("/log-out")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('Login'))

# END


# Add Product && Edit Product && View Product

def productId():
    pro_value = "PRO" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

    integer_value = random.randint(1000000, 9999999)

    if random.choice([True, False]):
        return pro_value
    else:
        return integer_value

@app.route("/add-product", methods=['POST', 'GET'])
def addProduct():
    product_id = productId()
    user = session.get('warehouse_name')
    
    if not user:
        flash("You need to log in first!", "error")
        return redirect(url_for('Login'))
    
    check_userData = authendication.query.filter_by(warehouse_name=user).first()
    
    if not check_userData:
        flash("User not found!", "error")
        return redirect(url_for('Login'))
    
    product_user_id = check_userData.product_user_id
        
    if request.method == 'POST':
        product_name = request.form.get('Product_name')
        product_amount = request.form.get('Product_amount')
        product_qty = request.form.get('Product_quantity')
        
        product_total_amount = float(product_amount) * int(product_qty)
        
        check_product = product.query.filter(product.product_user_id == product_user_id, product.product_name == product_name).first()

        if check_product:
            flash("Product already exists!", "error")
            return redirect(url_for('main'))

        
        dataSet = product(product_id=product_id, product_user_id=product_user_id, product_name=product_name, product_amount=product_amount, product_qty=product_qty,product_total_amount=product_total_amount)
        db.session.add(dataSet)
        db.session.commit()
        flash("Product created successfully!", 'success')
        return redirect(url_for('addProduct'))
    return render_template('Product/Product.html', product_id=product_id, product_user_id=product_user_id)


# Product Request && Response
# def mvm():
#     prefix = "MVM"
#     digits = ''.join(random.choices(string.digits, k=4))
#     letters = ''.join(random.choices(string.ascii_lowercase, k=3))
#     mvm_id = f"{prefix}{digits}{letters}"
#     return mvm_id

# @app.route("/req", methods=['POST', 'GET'])
# def req():
    
#     Movment_Id = mvm()
#     Status = "pending..,"
    
#     if request.method == 'POST':
#         product_qty = request.form.get()
#         warehouse_to_name = request.form.get()

if __name__ == '__main__':
    app.run(debug=True)