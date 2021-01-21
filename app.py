from app_config import app
from flask import url_for, request, redirect, render_template, flash
from database import db, User, Apartment, Comment
from forms import generate_password_hash, check_password_hash, \
    LoginForm, RegistrationForm, ApartmentForm, CommentForm
from login_manager import login_manager, login_required, login_user, \
    logout_user, current_user
import logging

db.create_all()
logging.basicConfig(filename='logs.log',
                    format='%(levelname)s  %(asctime)s : %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


# BASIC NAVIGATION
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# AUTHENTICATION
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data,
                                            method='sha256')
        )
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken!")
        elif User.query.filter_by(email=form.email.data).first():
            flash("Email already taken!")
        else:
            db.session.add(new_user)
            db.session.commit()
            login_user(User.query.filter_by(email=form.email.data).first(),
                       remember=False)
            flash("Registered Successfully!")
            return redirect(url_for('index'))
    
    return render_template('auth/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash("Logged in Successfully!")
                return redirect(url_for('index'))
            else:
                flash("Invalid Password!")
        else:
            flash("Invalid Username!")
    
    return render_template('auth/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# APARTMENTS
@app.route('/apartments/index')
def apartments():
    all_apartments = Apartment.query.all()
    return render_template('apartments/index.html', apartments=all_apartments)


@app.route('/apartments/create', methods=['GET', 'POST'])
def apartment_create():
    form = ApartmentForm()
    if form.validate_on_submit():
        new_apartment = Apartment(
            name=form.name.data,
            location=form.location.data,
            description=form.description.data
        )
        if Apartment.query.filter_by(location=form.location.data).first():
            flash("Apartment location already taken!")
        else:
            db.session.add(new_apartment)
            db.session.commit()
            apartment = Apartment.query.filter_by(name=form.name.data).first()
            flash("Apartment added Successfully!")
            return redirect(url_for('apartment_show',
                                    apartment_id=apartment.id))
    
    return render_template('apartments/create.html', form=form)


@app.route('/apartments/<int:apartment_id>/show')
def apartment_show(apartment_id):
    apartment = Apartment.query.filter_by(id=apartment_id).first()
    comments = Comment.query.filter_by(apartment_id=apartment_id).all()
    comment_form = CommentForm()
    if not apartment:
        return render_template('errors/404.html'), 404
    return render_template(
        'apartments/show.html', apartment=apartment,
        comments=comments, form=comment_form)


# COMMENTS
@app.route('/comments/create', methods=['POST'])
@login_required
def comment_create():
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            user_id=form.user_id.data,
            apartment_id=form.apartment_id.data,
            comment=form.comment.data
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added Successfully!")
    else:
        flash("Error adding the comment")

    return redirect(url_for('apartment_show',
                            apartment_id=form.apartment_id.data))


# ERROR CODE HANDLERS
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(405)
def page_not_found(e):
    return render_template('errors/405.html'), 405
