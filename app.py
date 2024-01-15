from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from newsapi import NewsApiClient
from flask_login import LoginManager, login_user, UserMixin, logout_user, current_user, login_required
from datetime import datetime
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, validators
# from flask_session import Session


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///mydb2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'
# app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdD_UspAAAAAEwCyYYTsrtyQA9ClZH5zG6JRWuc'
# app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdD_UspAAAAANGiJEIsYeKaoqteCaE9YTE0Xq8X'
# app.config['RECAPTCHA_OPTIONS'] = {'theme': 'black'}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
 
# class RegistrationForm(FlaskForm):
#     username = StringField('Username', [validators.DataRequired()])
#     password = PasswordField('Password', [validators.DataRequired()])
#     confirm_password = PasswordField('Confirm Password', [
#         validators.DataRequired(),
#         validators.EqualTo('password', message='Passwords must match')
#     ])
#     recaptcha = RecaptchaField()
#     submit = SubmitField('Register')

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60),unique=True,nullable=False)
    password = db.Column(db.String(100),nullable=False)
    fname = db.Column(db.String(100),nullable=False)
    lname = db.Column(db.String(100),nullable=False)
    username = db.Column(db.String(100),nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
    
class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return '<Todo %r>' % self.title
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/bbc_news')
def bbc_news():
    newsapi = NewsApiClient(api_key="b57366967c1d41818cc17445e446cf4b")
    topheadlines = newsapi.get_top_headlines(sources="bbc-news")

    articles = topheadlines['articles']

    desc = []
    news = []
    img = []
    con = []

    for i in range (len(articles)):
        myarticles = articles[i]

        news.append(myarticles['title'])
        desc.append(myarticles['description'])
        img.append(myarticles['urlToImage'])
        con.append(myarticles['content'])

    myList = zip(news, desc, img, con)

    return render_template('news.html', context=myList)

@app.route('/bbc_news_sport')
def bbc_news_sport():
    newsapi = NewsApiClient(api_key="b57366967c1d41818cc17445e446cf4b")
    topheadlines = newsapi.get_top_headlines(sources="bbc-sport")

    articles = topheadlines['articles']

    desc = []
    news = []
    img = []
    con = []

    for i in range (len(articles)):
        myarticles = articles[i]

        news.append(myarticles['title'])
        desc.append(myarticles['description'])
        img.append(myarticles['urlToImage'])
        con.append(myarticles['content'])

    myList = zip(news, desc, img, con)

    return render_template('news.html', context=myList)



@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route('/home')
def home():
    data = Todo.query.filter()
    return render_template("home.html", data=data)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()

#     if form.validate_on_submit():
#         email = form.email.data
#         password = form.password.data
#         fname = form.fname.data
#         lname = form.lname.data
#         username = form.username.data

#         user = User(email=email, password=password, fname=fname, lname=lname, username=username)
#         db.session.add(user)
#         db.session.commit()
#         flash('User has been registered successfully.', 'success')
#         return redirect('/login')

#     return render_template("register.html", form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        user = User(email=email,password=password,fname=fname,lname=lname,username=username)
        db.session.add(user)
        db.session.commit()
        flash('user has been registered successfully.','success')
        return redirect('/login')

    return render_template("register.html")

@app.route("/login", methods=(['GET','POST']))
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=username).first()
        if user and password==user.password:
            login_user(user)
            flash('Your username and password is correct','success')
            return redirect('/todo')
        else:
            flash('Invalid Credentials','danger')
            return redirect('/login')

    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/todo',methods=(['GET','POST']))
def todo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        todo = Todo(title=title,description=description, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        flash('Your post has been submitted successfully','success')
        return redirect('/home')
    return render_template('todo.html')

@app.route('/update_todo/<int:todo_id>', methods=['POST'])
def update_todo(todo_id):
    todo=Todo.query.get_or_404(todo_id)
    if request.method == 'POST':
        id = request.form.get('todo_id')
        new_title = request.form.get('new_title')
        new_description = request.form.get('new_description')
        todo.title = new_title if new_title else todo.title
        todo.description = new_description if new_description else todo.description
        todo.title = new_title
        todo.description = new_description
        db.session.commit()
        flash('Task updated successfully!','success')
    return redirect('/home')

@app.route('/delete_todo/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    remaining_todos = Todo.query.all()
    for index, remaining_todo in enumerate(remaining_todos, start=1):
        remaining_todo.id = index
    db.session.commit()
    flash(' Task deleted successfully! ','success')
    return redirect('/home')

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)