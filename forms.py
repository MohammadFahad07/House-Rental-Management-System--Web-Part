from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, DateField, SelectField, IntegerField, FloatField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from wtforms.fields.html5 import TelField, EmailField


# Sign up form to take inputs from users and validate
class SignUpForm(FlaskForm):
    FullName = StringField("",validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Full Name"})
    PhoneNumber = StringField("", validators=[InputRequired(), Length(min=6, max=15)], render_kw={"placeholder": "Phone Number"})
    UserType= SelectField("", validators=[InputRequired()], choices=[("tenant","tenant"),("landlord","landlord"),("admin","admin")])
    EmailAddress = EmailField("",validators=[InputRequired(), Email()], render_kw={"placeholder": "Email Address"})
    Password = PasswordField("", validators=[InputRequired(), Length(min=8,max=50)], render_kw={"placeholder": "Password"})
    Submit = SubmitField("Register")

# Login form to take email and password as input and validate before query
class LoginForm(FlaskForm):
    EmailAddress = EmailField("",validators=[InputRequired(), Email()], render_kw={"placeholder": "Email Address"})
    Password = PasswordField("", validators=[InputRequired(), Length(min=8,max=50)], render_kw={"placeholder": "Password"})
    Remember = BooleanField('Remember me')
    Submit = SubmitField("Login")


# Email subscriber form
class EmailSubscribeForm(FlaskForm):
    EmailAddress = EmailField("",validators=[InputRequired(), Email()], render_kw={"placeholder": "Email Address"})
    Submit = SubmitField("Subscribe")


# Add new product form
class ProductForm(FlaskForm):
    ProductName = StringField("",validators=[InputRequired(), Length(min=4, max=100)], render_kw={"placeholder": "Product name"})
    ProductDescription = TextAreaField("",validators=[InputRequired(), Length(min=4, max=300)], render_kw={"placeholder": "Product Description"})
    Price = IntegerField("", validators=[InputRequired()], render_kw={"placeholder": "Price"})
    Category = SelectField("", validators=[InputRequired()], choices=[])
    Submit = SubmitField("Add product")


# Category
class CategoryForm(FlaskForm):
    Name = StringField("", validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Category name"})
    Submit = SubmitField("Add category")


# Delivery address
class DeliveryAddressForm(FlaskForm):
    Name = StringField("", validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Receiver name"})
    Address = TextAreaField("",validators=[InputRequired(), Length(min=4, max=300)], render_kw={"placeholder": "Address"})
    Phone = IntegerField("", validators=[InputRequired()], render_kw={"placeholder": "Phone"})
    Submit = SubmitField("Done")    