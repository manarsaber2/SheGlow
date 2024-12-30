from flask import Flask ,render_template ,request ,redirect,url_for,flash,session,jsonify
from flask_sqlalchemy import SQLAlchemy
import pyodbc
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, SelectField,DecimalField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp
from datetime import datetime, timedelta 
from sqlalchemy import and_
from sqlalchemy.orm import relationship
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

app.config['SECRET_KEY']='your secret key'

app.config['SQLALCHEMY_DATABASE_URI'] =('mssql+pyodbc://@DESKTOP-VJJHOBL/project?'
                                        
'driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

db = SQLAlchemy(app)

class Client(db.Model):
    __tablename__ = 'client' 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100))
    second_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(15))
    wishlist = db.relationship('Wishlist', backref='client', lazy=True)


    def __init__(self, first_name, second_name, email, password, address, phone_number):
        self.first_name = first_name
        self.second_name = second_name
        self.email = email
        self.password = password
        self.address = address
        self.phone_number = phone_number

class Admin(db.Model):
    __tablename__ = 'adminn'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, user_name, email, password):
        self.user_name = user_name
        self.email = email
        self.password =password

class Product(db.Model):
    __tablename__ = 'Product'
    ProductID = db.Column(db.Integer, primary_key=True)
    ProductName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text, nullable=False)
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    StockQuantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    Brand = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    admin_id = db.Column(db.Integer, nullable=True)
    PhotoPath = db.Column(db.String(255), nullable=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    order_details = relationship('OrderDetails', back_populates='product')
    
    def __init__(self, ProductName, Description, Price, StockQuantity, category, Brand, rating, admin_id, PhotoPath):
    
        self.ProductName = ProductName
        self.Description = Description
        self.Price = Price
        self.StockQuantity = StockQuantity
        self.category = category
        self.Brand = Brand
        self.Rating = rating
        self.admin_id =admin_id
        self.PhotoPath = PhotoPath
    def __repr__(self):
     return f'<Product {self.ProductName}>'

class Order(db.Model):
    __tablename__ = 'orders'
    order_ID = db.Column(db.Integer, primary_key=True)
    order_status = db.Column(db.String(50))
    order_date = db.Column(db.DateTime)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    order_details = relationship('OrderDetails', back_populates='order')
    client = db.relationship('Client', backref=db.backref('orders', lazy=True))
    def __init__(self, order_status, client_id, order_date):
        self.order_status = order_status
        self.client_id = client_id
        self.order_date = order_date
    def __repr__(self):
        return f'<Order {self.order_ID} - {self.order_status}>'

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.ProductID'), nullable=False)
    product = db.relationship('Product', backref='wishlist', lazy=True)

    def __init__(self, client_id, product_id):
        self.client_id = client_id
        self.product_id = product_id

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.ProductID'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __init__(self, product_id, client_id, review_text, rating, user_name, email):
        self.product_id = product_id
        self.client_id = client_id
        self.review_text = review_text
        self.rating = rating
        self.user_name = user_name
        self.email = email

class RecentlyViewed(db.Model):
    __tablename__ = 'recently_viewed '
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.ProductID'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    client = db.relationship('Client', back_populates='recently_viewed')
    product = db.relationship('Product', back_populates='recently_viewed')

Client.recently_viewed = db.relationship('RecentlyViewed', back_populates='client')

Product.recently_viewed = db.relationship('RecentlyViewed', back_populates='product')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', [
        InputRequired(), 
        Length(min=3, max=50, message="First name must be between 3 and 50 characters.")
    ])
    second_name = StringField('Second Name', [
        InputRequired(),
        Length(min=3, max=50, message="Second name must be between 3 and 50 characters.")
    ])
    email = StringField('Email', [
        InputRequired(),
        Email(message="Please provide a valid email address.")
    ])
    password = PasswordField('Password', [
        InputRequired(),
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', [
        InputRequired(),
        EqualTo('password', message="Passwords must match.")
    ])
    address = StringField('Address', [InputRequired()])
    phone_number = StringField('Phone Number', [
        InputRequired(),
        Regexp(r'^\+?\d{1,15}$', message="Please enter a valid phone number.")
    ])
    submit = SubmitField('Register')

class ProductForm(FlaskForm):

    ProductName = StringField('Product Name', [InputRequired(), Length(min=3, max=100)])
    Description = StringField('Description', [InputRequired(), Length(min=10, max=500)])
    Price = DecimalField('Price', [InputRequired()], places=2) 
    StockQuantity = IntegerField('Stock Quantity', [InputRequired()])
    category = StringField('Category', [InputRequired(), Length(min=3, max=100)])
    Brand = StringField('Brand', [InputRequired(), Length(min=3, max=100)])
    rating = IntegerField('Rating', [InputRequired()])
    admin_id = IntegerField('Admin ID', [InputRequired()])
    PhotoPath = StringField('Photo Path')
    submit = SubmitField('Add Product')

class OrderDetails(db.Model):
    __tablename__ = 'OrderDetails'

    detail_ID = db.Column(db.Integer, primary_key=True)  # Unique ID for each order detail record
    order_ID = db.Column(db.Integer, db.ForeignKey('orders.order_ID'), nullable=False)  # Foreign key to Orders table
    product_id = db.Column(db.Integer, db.ForeignKey('Product.ProductID'), nullable=False)  # Foreign key to Product table
    product_Quantity = db.Column(db.Integer, nullable=False)  # Quantity of the product ordered
    Price = db.Column(db.Numeric(10, 2), nullable=False)  # Price of the product at the time of the order
    phone = db.Column(db.String(15))  # Phone number for the order (optional)
    address = db.Column(db.String(255))  # Shipping address for the order (optional)
    name = db.Column(db.String(100))  # Name of the product (redundant but can be useful for display)

    # Relationships to other tables
    order = relationship('Order', back_populates='order_details')
    product = relationship('Product', back_populates='order_details')

    def __init__(self, order_ID, product_id, product_Quantity,unit_price, phone, address, name):
        self.order_ID = order_ID
        self.product_id = product_id
        self.product_Quantity = product_Quantity
        self.Price = round(product_Quantity * unit_price,2)
        self.phone = phone
        self.address = address
        self.name = name

    def __repr__(self):
        return f'<OrderDetail {self.detail_ID} - {self.name}>'
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.ProductID'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    client = db.relationship('Client', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

    def __init__(self, client_id, product_id, quantity):
        self.client_id = client_id
        self.product_id = product_id
        self.quantity = quantity
        
       
@app.route('/')
def home():
    banners = [
        {
            'image': 'images/banner1.png',
            'heading': 'Get the Glow!',
            'subheading': 'Shop our exclusive skincare range.',
            'button_text': 'Shop Now',
            'button_url': '/product',
        },
        {
            'image': 'images/banner2.jpg',
            'heading': 'Winter Collection',
            'subheading': 'Stay warm with our new makeup collection.',
            'button_text': 'Shop Now',
            'button_url': '/product',
        },
        {
            'image': 'images/banner3.jpg',
            'heading': 'Fight the Signs of Aging',
            'subheading': 'Our anti-aging skincare collection will help you achieve younger, radiant skin.',
            'button_text': 'Shop Now',
            'button_url': '/product',
        },
        {
            'image': 'images/banner5.jpg',
            'heading': 'Candles Coming Soon!',
            'subheading': 'Our exclusive candle collection will be here soon. Stay tuned for the most enchanting scents!',
            'button_text': 'Shop Now',
            'button_url': '/product',
        },
        {
            'image': 'images/banner4.avif',
            'heading': 'Body Care Collection',
            'subheading': 'Nourish your skin with our range of lotions, body butters, and more.',
            'button_text': 'Shop Now',
            'button_url': '/product',
        },
        {
            'image': 'images/banner6.jpg',
            'heading': 'Silk and Waves Smooth Hair Brush Coming Soon!',
            'subheading': 'Achieve the smoothest hair with our upcoming Silk and Waves Hair Brush. Coming soon!',
            'button_text': 'Shop Now',
            'button_url': '/product',
        }
    ]  
    categories = [
    {"name": "Skin Care", "image": "images/skincare.p1.jpg", "button_text": "Explore Skin Care"},
    {"name": "Makeup", "image": "images/makeup.p1.jpg", "button_text": "Explore Makeup"}
] 

    products = Product.query.limit(4).all() 

    return render_template('index.html', banners=banners, categories=categories, products=products)

@app.route('/product/<string:product_cat>')
def products_by_category(product_cat):
    sort_by = request.args.get('sort_by', 'ProductName')  
    order = request.args.get('order', 'asc') 
    query = Product.query.filter(Product.category == product_cat)

    if sort_by == 'Price':
        query = query.order_by(Product.Price.asc() if order == 'asc' else Product.Price.desc())
    elif sort_by == 'Rating':
        query = query.order_by(Product.rating.asc() if order == 'asc' else Product.rating.desc())
    else:
        query = query.order_by(Product.ProductName.asc() if order == 'asc' else Product.ProductName.desc())

    category_products = query.all()
    return render_template('makeup.html', products=category_products, category=product_cat, sort_by=sort_by, order=order)

#manar
@app.before_request
def check_session_expiration():
  
    if 'login_time' in session and request.endpoint != 'login':
    
        login_time = session['login_time']

        if login_time.tzinfo is not None: 
            login_time = login_time.replace(tzinfo=None)  

        if datetime.now() - login_time > timedelta(days=7):
            session.clear()
            flash('Session expired. Please log in again.', 'error')  
            return redirect(url_for('login')) 
   
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'client_id' in session:
        return redirect(request.referrer or '/')

    if request.method == 'POST':
        email= request.form['email']
        password = request.form['password']

       
        client = Client.query.filter_by(email=email).first()

     
        if client and client.password == password:
            session['login_time'] = datetime.now()
            session['client_id'] = client.id
            session.permanent = True
            flash('Login successful!', 'success')
            return render_template('index.html') 
         
        flash('Invalid email or password, please try again.', 'error')  
        return redirect(request.referrer or '/create')  

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('client_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(request.referrer or url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

      
        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('forgot_password'))

      
        client = Client.query.filter_by(email=email).first()
        if client:
            client.password = new_password
            db.session.commit()
            flash("Password updated successfully. Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("No account found with that email.", "error")
            return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    form = RegisterForm()
    if form.validate_on_submit():
        
        if form.password.data != form.confirm_password.data:
            flash('Passwords do not match, please try again.', 'error')
            return redirect(url_for('create'))

        
        new_client = Client(
            first_name=form.first_name.data,
            second_name=form.second_name.data,
            email=form.email.data,
            password=form.password.data, 
            address=form.address.data,
            phone_number=form.phone_number.data
        )
        db.session.add(new_client)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('home'))

    return render_template('create.html', form=form)


@app.route('/product', methods=['GET'])
def show_products():
    sort_by = request.args.get('sort_by', 'ProductName')  
    order = request.args.get('order', 'asc')  

    if sort_by == 'Price':
        products = Product.query.order_by(Product.Price.asc() if order == 'asc' else Product.Price.desc()).all()
    elif sort_by == 'Rating':
        products = Product.query.order_by(Product.rating.asc() if order == 'asc' else Product.rating.desc()).all()
    else:  
        products = Product.query.order_by(Product.ProductName.asc() if order == 'asc' else Product.ProductName.desc()).all()

    client_id = session.get('client_id')  
    wishlist = set()  
    if client_id:
        wishlist = set(item.product_id for item in Wishlist.query.filter_by(client_id=client_id).all())


    return render_template( 'product.html', products=products, sort_by=sort_by, order=order, wishlist=wishlist)

#sama
@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.timestamp.desc()).all()

    if 'client_id' not in session:
        flash('Please log in to view your recently viewed products.', 'error')
        return redirect(request.referrer or url_for('login'))

    client_id = session['client_id']

   
    client_recently_viewed = RecentlyViewed.query.filter_by(client_id=client_id).order_by(RecentlyViewed.timestamp.asc()).all()

    if len(client_recently_viewed) >= 5:
      
        oldest_entry = client_recently_viewed[0]
        db.session.delete(oldest_entry)
        db.session.commit()

   
    new_recently_viewed = RecentlyViewed(client_id=client_id, product_id=product_id)
    db.session.add(new_recently_viewed)
    db.session.commit() 

   
    recently_viewed_products = RecentlyViewed.query.filter_by(client_id=client_id).order_by(RecentlyViewed.timestamp.desc()).limit(5).all()
    recently_viewed_product_ids = [entry.product_id for entry in recently_viewed_products]
    products = Product.query.filter(Product.ProductID.in_(recently_viewed_product_ids)).all()

    if request.method == 'POST':
        review_text = request.form.get('review_text')
        rating = request.form.get('rating')
        user_name = request.form.get('user_name')
        email = request.form.get('email')

        if review_text and rating and user_name:
            new_review = Review(
                product_id=product_id,
                client_id=client_id,
                review_text=review_text,
                rating=int(rating),
                user_name=user_name,
                email=email
            )
            db.session.add(new_review)
            db.session.commit()
            flash('Review added successfully!', 'success')
            return redirect(url_for('product_details', product_id=product_id))

    return render_template(
        'product_details.html',
        product=product,
        reviews=reviews,
        recently_viewed=products,
    )

#manar
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')  
    if query:

        results = Product.query.filter(Product.ProductName.ilike(f'%{query}%')).all()
    else:
        results = [] 
    
    return render_template('search.html', products=results)

@app.route('/search_suggestions', methods=['GET'])
def search_suggestions():
    query = request.args.get('q', '')
    if query:
       
        results = Product.query.filter(Product.ProductName.ilike(f'%{query}%')).limit(5).all()
        suggestions = [{'ProductName': product.ProductName} for product in results]
    else:
        suggestions = []

    return jsonify(suggestions)


#menna
@app.route('/update_orders', methods=['GET'])
def update_orders():
    try:
        cutoff_date = datetime.now() - timedelta(days=2)
        pending_orders = Order.query.filter(Order.order_status == 'Pending', Order.order_date <= cutoff_date).all()
        for order in pending_orders:
            order.order_status = 'Completed'
        db.session.commit()
        return jsonify({"message": f"Updated {len(pending_orders)} orders to 'Completed'."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/order-tracking/<int:order_id>', methods=['GET'])
def track_order(order_id):
    if 'client_id' not in session:
        return jsonify({"error": "Please log in to track your order"}), 401  
        


    client_id = session['client_id']
    order = Order.query.get(order_id)

    if not order or order.client_id != client_id:
       return jsonify({"error": "Order not found or unauthorized access", "flash": "Order not found or unauthorized access"}), 404
    
    order_status = order.order_status
    order_date = order.order_date
    if isinstance(order_date, datetime):
        order_date = order_date.date()

    days_since_order = (datetime.now().date() - order_date).days
    if order_status == "Pending" and days_since_order > 2:
        order.order_status = "Completed"
        db.session.commit()
        order_status = "Completed"

    return jsonify({
        "order_id": order_id,
        "order_status": order_status,
        "order_date": order_date.strftime("%Y-%m-%d"),
        "days_since_order": days_since_order
    })

@app.route('/order-tracking', methods=['GET'])
def track_order_page():
    return render_template('order-tracking.html')


@app.route('/request_return_or_exchange', methods=['POST'])
def request_return_or_exchange():
    try:
        email = request.form.get('email')
        if not email:
            return jsonify({"message": "Email is required"}), 400

        
        sender_email = "menoemail305@gmail.com"
        sender_password = "pybr sgfm cdqc wlme"
        subject = "Return or Exchange Request Confirmation"
        
       
        body = """\
        <html>
            <body>
                <p>Dear Customer,</p>
                <p>Thank you for reaching out to us. We have received your request for a return or exchange. Our representative will contact you shortly to assist you with the process.</p>
                <p>Best regards,<br>
                <span style="color:black; font-weight:bold;">SHE</span><span style="color:#D91656; font-weight:bold;">GLOW</span> Team</p>
            </body>
        </html>
        """

        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))  

     
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())

        return jsonify({"message": "Email sent successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/refund-policy')
def refund():
    return render_template('refund-policy.html')
@app.route('/shipping-policy')
def shipping():
    return render_template('shipping-policy.html')
@app.route('/privacy-policy')
def privacy():
    return render_template('privacy-policy.html')


#manar
@app.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
def toggle_wishlist(product_id):
    if 'client_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please log in to manage your wishlist.'}), 401

    client_id = session['client_id']

    # Check if the product is already in the wishlist
    existing_item = Wishlist.query.filter_by(client_id=client_id, product_id=product_id).first()
    if existing_item:
        db.session.delete(existing_item)
        db.session.commit()
        return jsonify({'status': 'success', 'action': 'removed', 'message': 'Product removed from wishlist.'})
    else:
        new_item = Wishlist(client_id=client_id, product_id=product_id)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'status': 'success', 'action': 'added', 'message': 'Product added to wishlist!'})

@app.route('/wishlist', methods=['GET','POST'])
def wishlist():
    if 'client_id' not in session:
        flash('Please log in to view your wishlist.', 'error')
        return redirect(url_for('login'))

    client_id = session['client_id']
    wishlist_items = Wishlist.query.filter_by(client_id=client_id).all()
    return render_template('wishlist.html', wishlist_items=wishlist_items)


#rana

@app.route('/dashboard')
def dashboard():
    client_id = session.get('client_id')
    if not client_id:
        return redirect(url_for('login')) 

   
    client = Client.query.get(client_id)
    
    
    orders = Order.query.filter_by(client_id=client_id).all()
    order_history = []

   
    for order in orders:
        order_details = OrderDetails.query.filter_by(order_ID=order.order_ID).all()
        products = []
        
        for detail in order_details:
            product = Product.query.get(detail.product_id)  
            products.append({
                'name': product.ProductName,
                'quantity': detail.product_Quantity,
                'price': detail.Price,
                'image_url': product.PhotoPath 
            })
        
        order_history.append({
            'order_id': order.order_ID,
            'order_date': order.order_date,
            'status': order.order_status,
            'products': products
        })

    return render_template('dashboard.html', client=client, order_history=order_history)

@app.route('/update_address', methods=['POST'])
def update_address():
    if 'client_id' not in session:
        return jsonify({"success": False, "message": "Please log in to update your address."}), 401

    data = request.get_json()
    new_address = data.get('address')

    if not new_address:
        return jsonify({"success": False, "message": "Address cannot be empty."}), 400

    
    client = Client.query.get(session['client_id'])
    if not client:
        return jsonify({"success": False, "message": "Client not found."}), 404

    try:
     
        client.address = new_address
        db.session.commit()
        return jsonify({"success": True, "message": "Address updated successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500
    
    
#Shahd
def get_cart(client_id):
    return CartItem.query.filter_by(client_id=client_id).all()


# Routes
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'client_id' not in session:
        flash('Please log in to view your cart.', 'error')
        return redirect( request.referrer or url_for('login'))

    client_id = session['client_id']
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect( url_for('add_to_cart_page'))

    cart_item = CartItem.query.filter_by(client_id=client_id, product_id=product_id).first()
    if cart_item:
        if cart_item.quantity + 1 > product.StockQuantity:
            flash(f'Sorry, only {product.StockQuantity} of "{product.ProductName}" are available.', 'error')
            return redirect(request.referrer or url_for('add_to_cart_page'))
        cart_item.quantity += 1
    else:
        if 1 > product.StockQuantity:
            flash(f'Sorry, only {product.StockQuantity} of "{product.ProductName}" are available.', 'error')
            return redirect( url_for('add_to_cart_page'))
        new_item = CartItem(client_id=client_id, product_id=product_id, quantity=1)
        db.session.add(new_item)

    db.session.commit()
    flash(f'Product "{product.ProductName}" added to your cart.', 'success')
    return redirect(request.referrer or url_for('add_to_cart_page'))


@app.route('/add_to_cart_page')
def add_to_cart_page():
    if 'client_id' not in session:
        flash('Please log in to view your cart.', 'error')
        return redirect(request.referrer or url_for('login'))
    
    client_id = session['client_id']
   
    cart_items = CartItem.query.filter_by(client_id=client_id).all()
    if not cart_items:
        return render_template('add_to_cart_page.html', cart_items=[], total=0)

    items_with_quantity = []
    total = 0
    for cart_item in cart_items:
        product = cart_item.product  
        product.quantity = cart_item.quantity
        product.subtotal = product.quantity * float(product.Price)
        total += product.subtotal
        items_with_quantity.append(product)

    total = round(total, 2)
    return render_template('add_to_cart_page.html', cart_items=items_with_quantity, total=total)


@app.route('/decrease_quantity/<int:product_id>', methods=['POST'])
def decrease_quantity(product_id):
    client_id = session['client_id']

    cart_item = CartItem.query.filter_by(client_id=client_id, product_id=product_id).first()

    if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()
            
    else:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Product removed from cart.', 'success')
  

    return redirect(url_for('add_to_cart_page'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
   
    client_id = session['client_id']

    cart_item = CartItem.query.filter_by(client_id=client_id, product_id=product_id).first()
   
    db.session.delete(cart_item)
    db.session.commit()
    flash('Product removed from the cart.', 'success')
    

    return redirect(url_for('add_to_cart_page'))


@app.route('/clear_cart', methods=['POST'])
def clear_cart():
   
    client_id = session['client_id']
    
    CartItem.query.filter_by(client_id=client_id).delete()
    db.session.commit()

    flash('All products removed from the cart successfully.', 'success')
    return redirect(url_for('add_to_cart_page'))



#shahd part2
@app.route('/checkout', methods=['GET'])
def checkout():
    client_id = session['client_id']
    cart_items = get_cart(client_id)
    if not cart_items:
        return redirect(url_for('add_to_cart_page'))

    total = 0
    product_details = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            item.product = product
            item.subtotal = item.quantity * float(product.Price)
            total += item.subtotal

            product_details.append({
                'PhotoPath': product.PhotoPath,
                'ProductName': product.ProductName,
                'Price': round(float(product.Price), 2),
                'quantity': item.quantity,
                'subtotal': round(item.subtotal, 2)
            })

    shipping_cost = 50
    total_with_shipping = round(total + shipping_cost, 2)

    return render_template(
        'checkout.html',
        cart_items=product_details,
        total=round(total, 2),
        shipping_cost=shipping_cost,
        total_with_shipping=total_with_shipping
    )

#shahd Part_3
@app.route('/complete_order', methods=['POST','GET'])
def complete_order():
    
    client_id = session.get('client_id')
    cart_items = get_cart(client_id)
    if not cart_items:
        flash('Your cart is empty. Please add products before completing the order.', 'error')
        return redirect(url_for('add_to_cart_page'))

    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')

    if not all([name, phone, address]):
        flash('Please enter all the required information.', 'error')
        return redirect(url_for('checkout'))

    new_order = Order(order_status="Pending", client_id=client_id, order_date=datetime.now())
    db.session.add(new_order)
    db.session.commit()

    for item in cart_items:
        product = Product.query.get(item.product_id)
        if item.quantity > product.StockQuantity:
            flash(f'Sorry, product "{product.ProductName}" is only available in quantity {product.StockQuantity}.', 'error')
            return redirect(url_for('checkout'))

        product.StockQuantity -= item.quantity
        order_detail = OrderDetails(
            order_ID=new_order.order_ID,
            product_id=item.product_id,
            product_Quantity=item.quantity,
            unit_price=product.Price,
            name=name,
            phone=phone,
            address=address
        )
        db.session.add(order_detail)

    db.session.commit()

   
    CartItem.query.filter_by(client_id=client_id).delete()
    db.session.commit()

    flash('Order completed successfully!', 'success')
    return redirect(url_for('checkout', order_id=new_order.order_ID))


@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
