from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "34jbh34bth43bt4"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

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
        return redirect(url_for("index",id=blog_id))

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