from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '8ghij938hy9gbh8gherg'

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(32), nullable=False, unique=True)
    password=db.Column(db.String(128),nullable=False)

class SignUpForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=5,max=32)],render_kw={"placeholder": "Username"})
    password=StringField(validators=[InputRequired(),Length(min=10,max=20)],render_kw={"placeholder": "Password"})
    submit=SubmitField("Register")
    
    def username_exists(self, username):
        existing_user_name=User.query.filter_by(username=username.data).first()
        if existing_user_name:
            raise ValidationError("Username already exists!")

class LogInForm(FlaskForm):
    username=StringField(validators=[InputRequired(),Length(min=5,max=32)],render_kw={"placeholder": "Username"})
    password=StringField(validators=[InputRequired(),Length(min=10,max=20)],render_kw={"placeholder": "Password"})
    submit=SubmitField("Login")
    

@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    f=LogInForm()
    return render_template('login.html',form=f)

@app.route('/signup', methods=['GET','POST'])
def signup():
    f=SignUpForm()
    return render_template('signup.html',form=f)

if __name__ == '__main__':
    app.run(debug=True)
