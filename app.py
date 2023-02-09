from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Shanghai')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(12))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.all()                                  #将Post数据库中的值全部取出，保存到posts
        return render_template("index.html", posts=posts)         #将posts的值传递给index.html页面


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User(username=username, password=generate_password_hash(password, method='sha256'))

        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template("signup.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
    else:
        return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':                     #如果是POST方法
        title = request.form.get('title')            #将表格title字段存入title
        content = request.form.get('content')        #将表格的content字段存入content

        post = Post(title=title, content=content)     #将所有值存入post

        db.session.add(post)                       #将post保存值存入db数据库
        db.session.commit()                        #提交保存对应值
        return redirect('/')
    else:
        return render_template("create.html")

@app.route("/<int:id>/update", methods=['GET', 'POST'])   #int类型的id
@login_required
def update(id):
    post = Post.query.get(id)                      #从Post数据库中取出指定id的数据
    if request.method == 'GET':
        return render_template("update.html", post=post)   #转到update页，将刚才取出的数据代入对应页面
    else:
        post.title = request.form.get('title')
        post.content = request.form.get('content')

        db.session.commit()
        return redirect('/')

@app.route("/<int:id>/delete", methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5050", debug=False)