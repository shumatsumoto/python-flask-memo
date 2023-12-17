from flask import Flask
from flask import render_template, g, redirect, request
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user

import sqlite3
DATABASE="flaskmemo.db"
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, userid):
        self.id = userid

#ログイン
@login_manager.user_loader
def load_user(userid):
    return User(userid)
@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/login")

#ログアウト
@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect("/login")

@app.route("/login", methods=['GET','POST'])
def login():
    error_message = ""
    userid = ""

    if request.method == "POST":
        userid = request.form.get("userid")
        password = request.form.get("password")
        # ログインのチェック
        if (userid == "shu" and password == "1234"):
            user = User(userid)
            login_user(user)
            return redirect("/")
        else:
            error_message = "入力された情報が間違ってます"

    return render_template("login.html", userid=userid, error_message=error_message)

@app.route("/")
@login_required
def top():
    memo_list = get_db().execute("select id, title, body from memo").fetchall()
    return render_template("index.html", memo_list=memo_list)

@app.route("/regist",methods=['GET','POST'])
@login_required
def regist():
    if request.method =='POST':
        #画面からの登録情報の取得
        title = request.form.get('title')
        body = request.form.get('body')
        db = get_db()
        db.execute("insert into memo (title,body) values(?,?)",[title,body])
        db.commit()
        return redirect('/')
    
    return render_template('regist.html')

@app.route("/<id>/edit", methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method =='POST':
        #画面からの登録情報の取得
        title = request.form.get('title')
        body = request.form.get('body')
        db = get_db()
        db.execute("update memo set title=?, body=? where id=?",[title,body,id])
        db.commit()
        return redirect('/')

    post = get_db().execute(
        "select id, title, body from memo where id=?",(id,)
    ).fetchone()
    return render_template("edit.html", post=post)

@app.route("/<id>/delete", methods=['GET', 'POST'])
@login_required
def delete(id):
    if request.method =='POST':
        #画面からの登録情報の取得
        db = get_db()
        db.execute("delete from memo where id=?",(id,))
        db.commit()
        return redirect('/')

    post = get_db().execute(
        "select id, title, body from memo where id=?",(id,)
    ).fetchone()
    return render_template("delete.html", post=post)

if __name__ == "__main__":
    app.run()

#database
def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db