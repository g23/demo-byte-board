from flask import Flask, request, g, render_template, redirect, session

from db import get_db, close_db

from helpers import require_logged_in

import bcrypt

app = Flask(__name__)

app.secret_key = b'\x7f\x8e\xe1L\x17W\xf0\xef\xc6L_-\xd0\x98In' # gen'd via os.urandom(16)

@app.route("/")
def hello():
    username = session.get("username")
    c = get_db().cursor()
    users = c.execute("SELECT * FROM users")
    #g.db.close()
    return render_template("index.html",username=username, users=users)

# GET /users list all users if power_level > 9000 else redirect to /

# POST /users/new makes new user
@app.route("/users/new", methods=["POST"])
def new_user():
    username = request.form["username"]
    password = bytes(request.form["password"], "utf") # bcrypt doesn't like unicode
    email = request.form.get("email") # not required
    power_level = 9001 # temporarily
    # bcrypt the password and save it to the database
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    # get the sqlite cursor, also the db will be on the g object
    c = get_db().cursor()

    c.execute('''
        INSERT INTO users (username, pass, email, power_level)
        VALUES (?, ?, ?, ?)
    ''', (username, hashed, email, power_level))

    g.db.commit()
    g.db.close()
    return redirect("/")


# POST /users/login logs a user in adds them to session
@app.route("/users/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = bytes(request.form["password"], "utf")
    # bcrypt the password and verify it's correct
    c = get_db().cursor()
    user = c.execute("SELECT * FROM users WHERE username=?", [username]).fetchone()
    # check the hashed password
    if bcrypt.checkpw(password, user["pass"]):
        # cool! logged in, set the session
        print("correct password!")
        session["username"] = username
        session["user_id"] = user["id"]
    else:
        print("password failed")
    # either way, redirect to /
    return redirect("/")


# GET /users/logout removes the user from the session
@app.route("/users/logout")
def logout():
    session.pop("username", None)
    session.pop("user_id", None)
    return redirect("/")

# GET /topics lists all the topic posts
@app.route("/topics")
def topics():
    c = get_db().cursor()
    topics = c.execute('SELECT * FROM posts JOIN users ON posts.user_id = users.id WHERE is_topic = 1')
    return render_template("topics/index.html", topics=topics)

# POST /topics/new adds a new topic post
@app.route("/topics/new", methods=["POST"])
def new_topic():
    # make sure logged in
    if "user_id" not in session:
        return redirect("/")
    # get data
    title = request.form["title"]
    content = request.form["content"]
    is_topic = 1
    user_id = int(session["user_id"])
    # insert it into the db
    c = get_db().cursor()
    c.execute('''
        INSERT INTO posts (title, content, is_topic, user_id)
        VALUES (?, ?, ?, ?)
    ''', [title, content, is_topic, user_id])
    g.db.commit()
    g.db.close()

    return redirect("/topics")

# GET /topics/<int:id> gets all the posts for a given topic id
@require_logged_in
@app.route("/topics/<int:id>")
def show_topic(id):
    c = get_db().cursor()
    # first find the topic
    topic = c.execute("SELECT * FROM posts AS p JOIN users AS u ON p.user_id=u.id WHERE p.id=?", [id]).fetchone()
    # then find the posts
    posts = c.execute("SELECT * FROM posts AS p JOIN users AS u ON p.user_id=u.id WHERE p.topic_id=?", [id])
    return render_template("topics/view.html", topic=topic, posts=posts)

# POST /topics/<int:id> posts a reply to the given topic
@require_logged_in
@app.route("/topics/<int:id>", methods=["POST"])
def post_reply(id):
    # get the data
    title = request.form["title"]
    content = request.form["content"]
    is_topic = 0
    topic_id = id
    user_id = int(session["user_id"])
    # put in db
    c = get_db().cursor()
    c.execute('''
        INSERT INTO posts (title, content, is_topic, topic_id, user_id)
        VALUES (?, ?, ?, ?, ?)
    ''', [title, content, is_topic, topic_id, user_id])
    g.db.commit()
    g.db.close()
    return redirect("/topics/"+str(id))

# POST /posts/<int:id> updates the post if user_id is right
@require_logged_in
@app.route("/posts/<int:id>", methods=["POST"])
def edit_post(id):
    # get the post
    c = get_db().cursor()
    post = c.execute("SELECT * FROM posts WHERE id=?", [id]).fetchone()
    # make sure the user_id is right
    if session["user_id"] != post["user_id"]:
        return redirect("/")
    # ok so can make the edits
    title = request.form["title"]
    content = "Edited: "+request.form["content"]
    # add it to the db
    c.execute('''
        UPDATE posts
        SET title=?, content=?
        WHERE id=?
    ''', [title, content, post["id"]])
    g.db.commit()
    g.db.close()
    return redirect("/topics/"+str(post["topic_id"]))


# DELETE /posts/<int:id> deletes a post if user_id right, not a topic, unless power_level > 9000
@require_logged_in
@app.route("/posts/<int:id>/delete", methods=["DELETE"])
def delete_post(id):
    # make sure the post isn't a topic post and also the user is correct
    c = get_db().cursor()
    post = c.execute("SELECT * FROM posts WHERE id=?", [id]).fetchone()
    if post["is_topic"] == 1:
        return redirect("/")
    if session["user_id"] != post["user_id"]:
        return redirect("/")
    
    # ok, can delete it then
    c.execute("DELETE FROM posts WHERE id=?", [id])
    g.db.commit()
    g.db.close()
    return redirect("/topics/"+str(post["topic_id"]))
