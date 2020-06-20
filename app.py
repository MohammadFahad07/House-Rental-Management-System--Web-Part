from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms.validators import InputRequired, Email, Length
from forms import *
from io import BytesIO
import os

# Connecting to the database and ORM as known sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from database import *

import PyPDF2


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

##################################
# Database Connection
engine = create_engine('sqlite:///HRMS.db')
Base.metadata.bind = engine

# Creates the session
session = scoped_session(sessionmaker(bind=engine))

@app.teardown_request
def remove_session(ex=None):
    session.remove()


###############################
# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
######################################


@login_manager.user_loader
def load_user(user_id):
    user = session.query(Users).filter_by(ID = int(user_id)).first()
    return user


# Log out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# Password Reset
@app.route('/reset_password')
def reset_password():
    return 'password reset page'


# Registration System
@app.route('/register',  methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    signup_form = SignUpForm()
    if signup_form.validate_on_submit():
        hashed_password = generate_password_hash(signup_form.Password.data, method='sha256')
        newUser = Users(FullName=signup_form.FullName.data, PhoneNumber=signup_form.PhoneNumber.data, UserType = signup_form.UserType.data, EmailAddress=signup_form.EmailAddress.data, Password=hashed_password)
        session.add(newUser)
        session.commit()

        return redirect(url_for('login'))
    else: print('validation failed')

    return render_template('signup.html', signup_form = signup_form)


# Login System
@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    email_subscribe_form = EmailSubscribeForm()

    login_form = LoginForm()

    if login_form.validate_on_submit():
        tempUser = login_form.EmailAddress.data
        user = session.query(Users).filter_by(EmailAddress=tempUser).first()
        if user:
            if check_password_hash(user.Password, login_form.Password.data):
                login_user(user, remember=login_form.Remember.data)
                return redirect(url_for('dashboard'))
            else:
                flash("Password not correct")
                return redirect(url_for('login'))

    return render_template('login.html', login_form = login_form, email_subscribe_form = email_subscribe_form)


# Define User dashboard
@app.route('/dashboard')
@login_required
def dashboard():

    email_subscribe_form = EmailSubscribeForm()

    if current_user.UserType == 'tenant':
        return render_template('tenant_dashboard.html')
        

    elif current_user.UserType == 'landlord':
        products = session.query(Product).filter_by(Landlord=current_user.ID).all()
        return render_template('landlord_dashboard.html', products=products)
    elif current_user.UserType == 'admin':
        category_form = CategoryForm()
        categories = session.query(Category).all()
        reserves = session.query(Reserve).all()
        products = session.query(Product).all()

        all_products = []
        for product in products:
            single_product = {}
            print(product.Landlord)
            landlord = session.query(Users).filter_by(ID=product.Landlord).first()
            landlord_name = landlord.FullName
            print(landlord.FullName)
            single_product = {'landlord' : landlord_name,'product_id' : product.ID,'product_name' : product.ProductName, 'product_description': product.ProductDescription, 'product_price' : product.Price }
            print(single_product)
            all_products.append(single_product)

        return render_template('admin_dashboard.html',category_form=category_form,categories=categories, all_products=all_products)
    else:
        flash('Access Denied')
        return url_for('home')

#Catagory Drawer
@app.route('/category_products/<int:category_id>', methods=['GET', 'POST'])
def category_products(category_id):
    the_category = session.query(Category).filter_by(ID=category_id).first()
    products = session.query(Product).filter_by(Category=the_category.Name).all()
    return render_template('products_by_category.html', products=products)


# Add category only allowed for admin
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if current_user.UserType == 'admin':
        category_form = CategoryForm()
        if category_form.validate_on_submit():
            newCategory = Category(Name = category_form.Name.data)
            session.add(newCategory)
            session.commit()
            return redirect(url_for('dashboard'))
        else:
            
            return render_template('add_category.html', category_form=category_form)
    else:
        return 'Not allowed'

#Delete catagory only allowed for admin
@app.route('/delete_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    if current_user.UserType == 'admin':
        the_category = session.query(Category).filter_by(ID=category_id).first()
        session.delete(the_category)
        session.commit()
        return redirect(url_for('dashboard'))
    else:
        return 'Access deined'

# Add flat only allowed for Landlord
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.UserType == 'landlord':
        product_form = ProductForm()
        product_form.Category.choices = [(category.Name, category.Name) for category in session.query(Category).all()]
        if product_form.validate_on_submit():
            newProduct = Product(ProductName=product_form.ProductName.data, ProductDescription=product_form.ProductDescription.data, Category=product_form.Category.data, Price=product_form.Price.data, Landlord=current_user.ID)
            session.add(newProduct)
            session.commit()
            return redirect(url_for('dashboard'))
        else:
            print('Validation failed')
            return render_template('add_product.html', product_form=product_form)
    else:
        return 'Access denied'
        
#delete flat ads only for admin
@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def delete_product(product_id):
    if current_user.UserType == 'admin':
        the_product = session.query(Product).filter_by(ID=product_id).first()
        session.delete(the_product)
        session.commit()
        return redirect(url_for('dashboard'))
    else:
        return 'Access deined'


# Flat preview
@app.route('/product_preview')
def product_preview():
    email_subscribe_form = EmailSubscribeForm()
    return render_template('products_by_category.html', email_subscribe_form=email_subscribe_form)


# Reserve NOW
@app.route('/reserve_now/<int:product_id>', methods=['GET', 'POST'])
def reserve_now(product_id):
    reserve_form = DeliveryAddressForm()
    the_product = session.query(Product).filter_by(ID=product_id).first()

    if reserve_form.validate_on_submit():
        new_reserve = Reserve(ProductName=the_product.ProductName, ReceiverName=reserve_form.Name.data, PhoneNumber=reserve_form.Phone.data, Address=reserve_form.Address.data)
        session.add(new_reserve)
        session.commit()
        return redirect(url_for('thank_you'))
    return render_template('reserve_now.html',reserve_form=reserve_form, product=the_product)



##########################################
#Social Networking system


##################################
# ABOUT US PAGE
@app.route('/about')
def about():
    return render_template('about.html')


# CONTACT US PAGE
@app.route('/contact')
def contact():
    return render_template('contact.html')

#Events page
@app.route('/events')
def events():
    categories = session.query(Category).all()
    products = session.query(Product).all()
    all_products = []
    for product in products:
        single_product = {}
        print(product.Landlord)
        landlord = session.query(Users).filter_by(ID=product.Landlord).first()
        landlord_name = landlord.FullName
        print(landlord.FullName)
        single_product = {'landlord' : landlord_name,'product_id' : product.ID,'product_name' : product.ProductName, 'product_description': product.ProductDescription, 'product_price' : product.Price }
        print(single_product)
        all_products.append(single_product)

    return render_template('events.html', categories=categories, all_products=all_products)
        


# Homepage
@app.route('/')
def home():
    
    

    return render_template('index.html')

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')


##################################

# Main Function
if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.debug = True
    app.run(host='0.0.0.0', port=5000)