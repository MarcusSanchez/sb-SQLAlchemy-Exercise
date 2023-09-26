"""Blogly application."""

from flask import Flask, redirect, render_template, request
from models import db, connect_db, Users

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-" + \
                    "blue-symbol-people-person-generic--public-domain--21.png"

with app.app_context():
    connect_db(app)
    db.create_all()


@app.route('/')
def redirect_to_users():
    return redirect('/users')


@app.route('/users')
def render_users():
    users = Users.query.order_by(Users.last_name, Users.first_name).all()
    return render_template('users.jinja2', users=users)


@app.route('/users/new')
def users_new_form():
    return render_template('new.jinja2')


@app.route("/users/new", methods=["POST"])
def users_new():
    try:
        fn = request.form['first_name']
        ln = request.form['last_name']
    except KeyError:
        return render_template('error.jinja2', error="Missing form data")

    url = request.form.get('image_url', None)

    new_user = Users(
        first_name=fn,
        last_name=ln,
        image_url=url or DEFAULT_IMAGE_URL
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>')
def users_show(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")
    return render_template('show.jinja2', user=user)


@app.route('/users/<int:user_id>/edit')
def users_edit(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")
    if user.image_url == DEFAULT_IMAGE_URL:
        user.image_url = ""
    return render_template('edit.jinja2', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    try:
        fn = request.form['first_name']
        ln = request.form['last_name']
    except KeyError:
        return render_template('error.jinja2', error="Missing form data")

    url = request.form.get('image_url', None)

    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")

    user.first_name = fn
    user.last_name = ln
    user.image_url = url or DEFAULT_IMAGE_URL

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def users_destroy(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")

    db.session.delete(user)
    db.session.commit()

    return redirect("/users")
