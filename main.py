from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "34jbh34bth43bt4"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ["login","register","index","blog_list"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

@app.route("/login", methods=["POST","GET"])
def login():

    if request.method == "POST":
        email=request.form["username"]
        password=request.form["password"]
        user=User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["username"] = username
            flash("Logged in")
            print(session)
            return redirect("/newpost")
        else:
            flash("User/password incorrect or user does not exist", "error")

    return render_template("login.html")

@app.route("/register", methods=["POST","GET"])
def register():

    if request.method == "POST":
        username=request.form["username"]
        password=request.form["password"]
        vpassword=["vpassword"]

        #TODO:validate user

        existing_user = user=User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect("/")
        else:
            #TODO error message
            return "<h1>Duplicate user</h1>"

    return render_template("register.html")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/blog", methods=["POST", "GET"])
def index():

    if request.method == "POST":
        blog_title=request.form["title"]
        blog_body=request.form["body"]

        if not blog_title or not blog_body:
            if not blog_title:
                flash("Please enter a blog title.", "error")
            if not blog_body:
                flash("Please enter a new blog.", "error")
            return redirect("/newpost")

        new_blog=Blog(blog_title,blog_body)
        db.session.add(new_blog)
        db.session.commit()
        blog_id=new_blog.id
        return redirect("/blog?id=" + str(blog_id))

    blog_posts=Blog.query.order_by(Blog.pub_date.desc()).all()

    if request.method == "GET" and "id" in request.args:
        id=request.args.get("id")
        blog_id=Blog.query.filter_by(id=id).first()
        return render_template("blog_post.html", title="Blog Post", blog_id=blog_id)

    return render_template("index.html", title="Build a Blog", blog_posts=blog_posts)

@app.route("/newpost", methods=["GET"])
def newpost():

    return render_template("newpost.html", title="Add a New Blog Post")

if __name__=="__main__":
    app.run()